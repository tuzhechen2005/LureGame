#include "LureWorld.h"
#include "FishingVisuals.h"
#include "LureSave.h"
#include "Camera/CameraComponent.h"
#include "Components/AudioComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "UnrealClient.h"

void ALurePawn::Announce(const FString& Title,const FString& Detail,float Seconds,float Punch){
 EventTitle=Title;EventDetail=Detail;EventLife=EventDuration=Seconds;Impact=FMath::Max(Impact,Punch);
}
void ALurePawn::StartFight(){
 if(!ActiveFish)return;
 const float Timing=FMath::Clamp(PhaseTime/BiteWindow,0.f,1.f);
 HookQuality=FMath::Clamp(1.f-FMath::Abs(Timing-.43f)/.48f,.15f,1.f);
 Fight.Start(ActiveFish->Weight,ActiveFish->Species,HookQuality,DistanceMetres());
 HookFacingYaw=GetControlRotation().Yaw;HookFacingPitch=GetControlRotation().Pitch;
 FightBearing=(LurePosition-GetActorLocation()).GetSafeNormal2D();RodSideInput=RodLiftInput=0;
 Tension=Fight.Tension;Stamina=Fight.Energy;Reeling=false;SetPhase(EFishingPhase::Fighting);
 Announce(HookQuality>.8f?TEXT("漂亮刺鱼！"):TEXT("中鱼！"),HookQuality>.8f?TEXT("钩口扎实，准备应对第一轮冲刺"):TEXT("稳住张力，别给它松线的机会"),1.5f,1.f);
 PlayCue(TEXT("HookSet"));
 UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_HOOK quality=%.3f weight=%.2f distance=%.1f"),HookQuality,ActiveFish->Weight,Fight.Distance);
}
void ALurePawn::EndFight(bool Success,const FString& Reason){
 if(Success){
  if(Phase==EFishingPhase::Landed)return;
  if(bObserve)ToggleObserve();
  ++Catches;SetPhase(EFishingPhase::Landed);Reeling=false;StartCatchPresentation();
  RecordCatch();Announce(TEXT("拿下了！"),LastCatch,2.5f,.65f);
  UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_LANDED time=%.2f score=%d xp=%d"),Fight.Time,CatchScore,CatchXP);
 }else{
  const FString Lost=Reason;ResetCast();PlayCue(TEXT("Escape"));
  Announce(Lost,TEXT("调整泄力和压竿方向，再试一次"),3.f,.35f);Notice=Lost;
  UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_LOST %s"),*Lost);
 }
}
FString ALurePawn::CadenceHint() const{
 if(Reeling)return TEXT("正在匀收 · 停顿或轻抽，给追来的鱼一个出手机会");
 if(Clock-LastTwitch<.8f)return TEXT("拟饵刚刚变向 · 停一下，留意竿尖");
 return TEXT("停顿中 · 再次收线或轻抽，让拟饵重新活起来");
}
void ALurePawn::TickEncounter(float Dt){
 if(bMenuOpen)return;
 EventLife=FMath::Max(0.f,EventLife-Dt);Impact=FMath::FInterpTo(Impact,0.f,Dt,7.f);
 Camera->SetFieldOfView(80.f+Impact*4.f);
 if(AmbientAudio)AmbientAudio->SetVolumeMultiplier(Volume*.55f*(Phase==EFishingPhase::Bite?.25f:(Phase==EFishingPhase::Fighting?.65f:1.f)));
 if(DragAudio){
  const bool Run=Phase==EFishingPhase::Fighting&&Fight.IsSurging()&&!Fight.IsTelegraphing();
  DragAudio->SetVolumeMultiplier(Run?Volume*FMath::Clamp(Fight.Pull*.38f,.15f,.65f):0.f);
  DragAudio->SetPitchMultiplier(.8f+Fight.Pull*.25f);
 }
 if(Phase==EFishingPhase::Landing){
  Reeling=false;
  if(PhaseTime>4.f){
   Fight.Distance=7;Fight.Energy=.18f;SetPhase(EFishingPhase::Fighting);
   Announce(TEXT("它又挣开了一段！"),TEXT("重新稳住，再把它带到岸边"),2.f,.35f);
  }
  return;
 }
 if(Phase!=EFishingPhase::Fighting)return;
 FFightInput Input;Input.Drag=Drag;Input.bReeling=Reeling;
 const float MouseSide=FMath::FindDeltaAngleDegrees(HookFacingYaw,GetControlRotation().Yaw)/30.f;
 const float MouseLift=FMath::FindDeltaAngleDegrees(HookFacingPitch,GetControlRotation().Pitch)/25.f;
 float KeysSide=0,KeysLift=0;
 if(auto* PC=Cast<APlayerController>(GetController())){
  KeysSide=float(PC->IsInputKeyDown(EKeys::D))-float(PC->IsInputKeyDown(EKeys::A));
  KeysLift=float(PC->IsInputKeyDown(EKeys::W))-float(PC->IsInputKeyDown(EKeys::S));
 }
 Input.RodSide=RodSideInput=KeysSide!=0?KeysSide:FMath::Clamp(MouseSide,-1.f,1.f);
 Input.RodLift=RodLiftInput=KeysLift!=0?KeysLift:FMath::Clamp(MouseLift,-1.f,1.f);
 const EFightMove Before=Fight.Move;const bool WasDanger=Tension>1.f;
 Fight.Step(Dt,Input);Tension=Fight.Tension;Stamina=Fight.Energy;
 // Distance is radial line distance. Side movement changes bearing without
 // silently adding metres beyond the HUD value or the netting threshold.
 Fight.Distance=FMath::Max(5.9f,Fight.Distance);
 const FVector Side(-FightBearing.Y,FightBearing.X,0);
 const float Lateral=FMath::Clamp(Fight.LateralOffset,-Fight.Distance*.5f,Fight.Distance*.5f);
 const float Forward=FMath::Sqrt(FMath::Max(0.f,FMath::Square(Fight.Distance)-FMath::Square(Lateral)));
 LurePosition=GetActorLocation()+(FightBearing*Forward+Side*Lateral)*100;
 LurePosition.Z=Fight.JumpHeight>0?Fight.JumpHeight*100:(Fight.Move==EFightMove::Dive?-110.f:-25.f);
 if(Before!=Fight.Move){
  Announce(Fight.MoveName(),Fight.Instruction(),1.25f,Fight.Move==EFightMove::Recover?.1f:.35f);
  if(Fight.Move!=EFightMove::Recover && LurePosition.Z>-55.f){SplashPosition=LurePosition;SplashPosition.Z=0;SplashTime=Clock;SurfaceCue(LurePosition,.85f);}
 }
 if(!WasDanger&&Tension>1.f){PlayCue(TEXT("LineStrain"));Impact=.4f;}
 if(Fight.bBroken){EndFight(false,TEXT("断线了"));return;}
 if(Fight.bLost){EndFight(false,Fight.HookSecurity<=0?TEXT("脱钩了"):TEXT("鱼带走了全部余线"));return;}
 if(DistanceMetres()<6.f&&Fight.Energy<.18f){
  Fight.JumpHeight=0;LurePosition.Z=-12;
  SetPhase(EFishingPhase::Landing);Reeling=false;
  Announce(TEXT("带到岸边了！"),TEXT("按空格抄鱼，完成这场较量"),4.f,.5f);
 }
}

void ALurePawn::RunEncounterTest(){
 int32 Errors=0;auto Check=[&](bool B,const TCHAR* Label){UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_TEST %s: %s"),B?TEXT("PASS"):TEXT("FAIL"),Label);if(!B)++Errors;};
 FFishingFight Blind;Blind.Start(2.5f,0,.95f,24);
 for(int i=0;i<7200&&!Blind.bBroken&&!Blind.bLost;++i){FFightInput I;I.Drag=.75f;I.bReeling=true;Blind.Step(1.f/60.f,I);}
 Check(Blind.bBroken,TEXT("holding hard drag and reeling through runs breaks the line"));
 for(int Species=0;Species<4;++Species){
  FFishingFight Good;Good.Start(Species==2?4.f:1.5f,Species,.95f,24);
  for(int i=0;i<12000&&!Good.bBroken&&!Good.bLost&&!(Good.Distance<3.5f&&Good.Energy<.18f);++i){
   FFightInput I;I.bReeling=Good.Move==EFightMove::Recover||Good.Energy<.1f;
   I.Drag=Good.IsSurging()?.28f:.57f;I.RodSide=Good.RequiredSide();
   I.RodLift=Good.Move==EFightMove::Dive?1.f:(Good.Move==EFightMove::Jump?-1.f:0.f);
   Good.Step(1.f/60.f,I);
  }
  UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_POLICY species=%d time=%.1f distance=%.2f energy=%.3f line=%.3f hook=%.3f"),Species,Good.Time,Good.Distance,Good.Energy,Good.LineCondition,Good.HookSecurity);
  Check(!Good.bBroken&&!Good.bLost&&Good.Distance<3.5f&&Good.Energy<.18f,TEXT("responsive control can land each fish archetype"));
 }
 auto* F=Fish[0];const FVector Water(2000,0,-75);F->Initialize(Water+FVector(200,0,0),.2f);F->SetSpecies(0);
 FLurePresentation Presentation;Presentation.LureType=0;Presentation.RetrieveSpeed=180;
 bool Attack=false;for(int i=0;i<1800;++i)Attack|=F->Simulate(1.f/60.f,Water,true,Presentation);
 Check(!Attack,TEXT("monotonous retrieve does not guarantee a bite"));
 for(int i=0;i<1800&&!Attack;++i){float Cycle=FMath::Fmod(i/60.f,2.8f);Presentation.RetrieveSpeed=Cycle<1.4f?180:0;Presentation.PauseSeconds=Cycle<1.4f?0:Cycle-1.4f;Presentation.TwitchAge=Cycle;Attack|=F->Simulate(1.f/60.f,Water,true,Presentation);}
 Check(Attack,TEXT("changing retrieve cadence can convert a hesitant follower"));
 UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_TEST COMPLETE failures=%d"),Errors);
 FPlatformMisc::RequestExitWithStatus(false,Errors?1:0);
}

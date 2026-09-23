#include "LureWorld.h"
#include "FishingVisuals.h"
#include "LureSave.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/PlayerController.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"
#include "HAL/PlatformMisc.h"

void ALurePawn::RunShoreCapture(float Dt){
 struct FCapture {
  TWeakObjectPtr<ALurePawn> Pawn;
  float Start=0,RetrieveStart=0,PreviousClock=0,LastShot=-100;
  int32 Casts=0,Completed=0,LastCadence=-1;
  bool Started=false,Finished=false,Released=false;
  EFishingPhase Previous=EFishingPhase::Ready;
  TSet<FString> Shots;
 };
 static FCapture State;
 if(State.Pawn.Get()!=this || Clock<State.PreviousClock){State=FCapture();State.Pawn=this;}
 State.PreviousClock=Clock;
 if(State.Finished || Clock<1.f)return;
 auto Shot=[&](const TCHAR* Name){
  if(State.Shots.Contains(Name)||FScreenshotRequest::IsScreenshotRequested()||Clock-State.LastShot<.2f)return;
  const FString Path=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectSavedDir(),FString::Printf(TEXT("Shore-%s.png"),Name)));
  FScreenshotRequest::RequestScreenshot(Path,true,false);State.Shots.Add(Name);State.LastShot=Clock;
  UE_LOG(LogTemp,Display,TEXT("LURE_SHORE_CAPTURE frame=%s phase=%d elapsed=%.2f path=%s"),Name,int32(Phase),Clock-State.Start,*Path);
 };
 auto Finish=[&](bool Good,const TCHAR* Why){
  State.Finished=true;
  UE_LOG(LogTemp,Display,TEXT("LURE_SHORE_CAPTURE %s elapsed=%.2f casts=%d catches=%d released=%d population=%d scripted_inputs=true reason=%s"),
   Good?TEXT("PASS"):TEXT("FAIL"),Clock-State.Start,State.Casts,State.Completed,State.Released,Fish.Num(),Why);
  FPlatformMisc::RequestExitWithStatus(false,Good?0:1);
 };
 auto* PC=Cast<APlayerController>(GetController());
 if(!PC){Finish(false,TEXT("no controller"));return;}
 if(!State.Started){
  State.Started=true;State.Start=Clock;bMenuOpen=false;bStarted=true;
  SaveData->bFishingAssist=false;ResetCast();
  PC->SetControlRotation(FRotator(-7,10.6f,0));Camera->SetWorldRotation(PC->GetControlRotation());
  UE_LOG(LogTemp,Display,TEXT("LURE_SHORE_CAPTURE begin normal_population=true assist=false no_injected_bites=true"));
 }
 if(Clock-State.Start>210.f){Finish(false,TEXT("two natural catches and release did not finish before timeout"));return;}
 if(Phase!=State.Previous){
  if(Phase==EFishingPhase::Retrieving){State.RetrieveStart=Clock;State.LastCadence=-1;}
  if(Phase==EFishingPhase::Landed)++State.Completed;
  if(Phase==EFishingPhase::Ready && State.Previous==EFishingPhase::Releasing)State.Released=true;
  State.Previous=Phase;
 }
 switch(Phase){
 case EFishingPhase::Ready:
  if(Clock-State.Start>4.f)Shot(TEXT("Ready"));
  if(Clock-State.Start>6.f){
   if(State.Casts>=7){Finish(false,TEXT("cast budget exhausted"));return;}
   // Fixed player decisions, not a hidden fish-position query. Subsequent
   // casts explore nearby cover rather than targeting a resting individual.
   const float Yaws[]={10.6f,21.f,-6.f,35.f,3.f,15.f,-10.f};
   PC->SetControlRotation(FRotator(-7,Yaws[State.Casts],0));Camera->SetWorldRotation(PC->GetControlRotation());
   ++State.Casts;PressCast();
  }
  break;
 case EFishingPhase::Charging:if(PhaseTime>(State.Casts==1?.34f:.55f))ReleaseCast();break;
 case EFishingPhase::Flying:ReelStop();break;
 case EFishingPhase::Retrieving:{
  const float Elapsed=Clock-State.RetrieveStart;
  const int32 Cadence=FMath::FloorToInt(Elapsed/3.4f);
  const float In=FMath::Fmod(Elapsed,3.4f);
  if(In<1.25f)ReelStart();else ReelStop();
  if(In>=1.3f && State.LastCadence!=Cadence){State.LastCadence=Cadence;Strike();}
  if(Clock-CueTime>.2f && Clock-CueTime<.7f)Shot(TEXT("Surface"));
  if(Elapsed>40)ResetCast();
  break;
 }
 case EFishingPhase::Bite:
  if(PhaseTime>.17f)Shot(TEXT("Bite"));
  if(PhaseTime>.34f)Strike();
  break;
 case EFishingPhase::Fighting:{
  // A repeatable reference control policy, not a claim of a human playtest.
  Drag=Fight.IsSurging()?.3f:.56f;
  if(Fight.Move==EFightMove::Recover || Fight.Energy<.12f)ReelStart();else ReelStop();
  const float Pitch=Fight.Move==EFightMove::Dive?25.f:(Fight.Move==EFightMove::Jump?-25.f:0.f);
  PC->SetControlRotation(FRotator(HookFacingPitch+Pitch,HookFacingYaw+Fight.RequiredSide()*30.f,0));
  if(PhaseTime>2)Shot(TEXT("Fight"));
  break;
 }
 case EFishingPhase::Landing:
  PC->SetControlRotation(FRotator(HookFacingPitch,HookFacingYaw,0));
  if(PhaseTime>.3f)Shot(TEXT("Landing"));
  if(PhaseTime>.7f)Strike();
  break;
 case EFishingPhase::Landed:
  if(PhaseTime>2.f)Shot(State.Completed==1?TEXT("Catch"):TEXT("SecondCatch"));
  if(PhaseTime>3.f && State.Completed==1 && !bObserve)ToggleObserve();
  if(PhaseTime>4.f && State.Completed==1)Shot(ActiveFish && ActiveFish->Species==1?TEXT("PerchDetail"):TEXT("FishDetail"));
  if(PhaseTime>5.5f){
   if(State.Completed>=2 && State.Released)Finish(true,TEXT("two natural catches, net support, inspection and release"));
   else ReleaseOrResetCast();
  }
  break;
 case EFishingPhase::Releasing:if(PhaseTime>.8f)Shot(TEXT("Release"));break;
 }
}

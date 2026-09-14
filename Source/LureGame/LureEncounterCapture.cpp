#include "LureWorld.h"
#include "FishingVisuals.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/PlayerController.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "Misc/Paths.h"
#include "UnrealClient.h"

namespace {
struct FEncounterCaptureState {
 TWeakObjectPtr<ALurePawn> Pawn;
 bool bStarted=false,bFinished=false,bSawBite=false,bSawFight=false;
 float PreviousClock=0,StartTime=0,RetrieveStart=-1,LastScreenshot=-100;
 int32 Attempts=0,PreviousCadence=-1;
 EFishingPhase PreviousPhase=EFishingPhase::Ready;
 TSet<FString> Screenshots;
};
}

void ALurePawn::RunEncounterCapture(float Dt) {
 if(!FParse::Param(FCommandLine::Get(),TEXT("LureEncounterCapture")))return;
 // This is a scripted player fixture. Every bite still has to come from
 // ALureFish::Simulate; the fixture never assigns a fish or a combat phase.
 static FEncounterCaptureState State;
 if(State.Pawn.Get()!=this || Clock<State.PreviousClock){
  State=FEncounterCaptureState();State.Pawn=this;
 }
 State.PreviousClock=Clock;
 if(State.bFinished || Clock<1.f)return;
 auto Finish=[&](bool bSuccess,const TCHAR* Reason){
  if(State.bFinished)return;
  State.bFinished=true;ReelStop();
  UE_LOG(LogTemp,Display,TEXT("LURE_ENCOUNTER_CAPTURE %s elapsed=%.2f casts=%d natural_bite=%s fight=%s screenshots=%d reason=%s scripted_inputs=true"),
   bSuccess?TEXT("PASS"):TEXT("FAIL"),Clock-State.StartTime,State.Attempts,
   State.bSawBite?TEXT("true"):TEXT("false"),State.bSawFight?TEXT("true"):TEXT("false"),State.Screenshots.Num(),Reason);
  FPlatformMisc::RequestExitWithStatus(false,bSuccess?0:1);
 };
 auto Screenshot=[&](const TCHAR* Name){
  const FString Key(Name);
  if(State.Screenshots.Contains(Key) || Clock-State.LastScreenshot<.12f || FScreenshotRequest::IsScreenshotRequested())return;
  const FString Filename=FPaths::ConvertRelativePathToFull(FPaths::Combine(FPaths::ProjectSavedDir(),FString::Printf(TEXT("Encounter-%s.png"),Name)));
  FScreenshotRequest::RequestScreenshot(Filename,true,false);
  State.Screenshots.Add(Key);State.LastScreenshot=Clock;
  UE_LOG(LogTemp,Display,TEXT("LURE_ENCOUNTER_CAPTURE frame=%s phase=%d time=%.2f distance=%.2f tension=%.3f energy=%.3f path=%s"),
   Name,int32(Phase),Clock-State.StartTime,DistanceMetres(),Tension,Fight.Energy,*Filename);
 };
 APlayerController* PC=Cast<APlayerController>(GetController());
 if(!PC){Finish(false,TEXT("missing player controller"));return;}
 if(!State.bStarted){
  State.bStarted=true;State.StartTime=Clock;
  bMenuOpen=false;bStarted=true;MenuPage=0;
  ResetCast();
  PC->SetControlRotation(FRotator(-7,0,0));
  Camera->SetWorldRotation(FRotator(-7,0,0));
  State.PreviousPhase=Phase;
  UE_LOG(LogTemp,Display,TEXT("LURE_ENCOUNTER_CAPTURE begin scripted_inputs=true natural_fish_ai=true timeout_game_seconds=120"));
 }
 if(Clock-State.StartTime>120.f){Finish(false,TEXT("natural encounter did not reach a trophy before deadline"));return;}
 if(Phase!=State.PreviousPhase){
  UE_LOG(LogTemp,Display,TEXT("LURE_ENCOUNTER_CAPTURE phase=%d previous=%d time=%.2f"),int32(Phase),int32(State.PreviousPhase),Clock-State.StartTime);
  if(Phase==EFishingPhase::Retrieving){State.RetrieveStart=Clock;State.PreviousCadence=-1;}
  if(Phase==EFishingPhase::Ready && State.bSawFight){Finish(false,TEXT("fish lost during adaptive fight"));return;}
  State.PreviousPhase=Phase;
 }
 switch(Phase){
  case EFishingPhase::Ready:
   // Let texture streaming settle before the first screenshot and cast.
   if(Clock-State.StartTime>=4.f)Screenshot(TEXT("Ready"));
   if(Clock-State.StartTime>=5.f){
    if(State.Attempts>=3){Finish(false,TEXT("three casts completed without landing"));return;}
    PC->SetControlRotation(FRotator(-7,0,0));Camera->SetWorldRotation(FRotator(-7,0,0));
    ++State.Attempts;PressCast();
    UE_LOG(LogTemp,Display,TEXT("LURE_ENCOUNTER_CAPTURE cast=%d yaw=0 pitch=-7 charge_seconds=0.6"),State.Attempts);
   }
   break;
  case EFishingPhase::Charging:
   if(PhaseTime>=.6f)ReleaseCast();
   break;
  case EFishingPhase::Flying:
   ReelStop();
   break;
  case EFishingPhase::Retrieving: {
   if(State.RetrieveStart<0)State.RetrieveStart=Clock;
   const float RetrieveTime=Clock-State.RetrieveStart;
   const int32 Cadence=FMath::FloorToInt(RetrieveTime/2.8f);
   const float InCadence=FMath::Fmod(RetrieveTime,2.8f);
   if(InCadence<1.4f)ReelStart();else ReelStop();
   // One deliberate twitch at the start of every second pause, never spam.
   if(InCadence>=1.4f && State.PreviousCadence!=Cadence){
    State.PreviousCadence=Cadence;
    if((Cadence%2)==1)Strike();
   }
   for(const ALureFish* F:Fish){
    if(F && (F->Behavior==EFishBehavior::Following || F->Behavior==EFishBehavior::Hesitating) && F->InterestLevel>.2f){Screenshot(TEXT("Follow"));break;}
   }
   break;
  }
  case EFishingPhase::Bite:
   State.bSawBite=true;ReelStop();
   if(PhaseTime>=.1f)Screenshot(TEXT("Bite"));
   if(PhaseTime>=BiteWindow*.43f)Strike();
   break;
  case EFishingPhase::Fighting: {
   State.bSawFight=true;
   Drag=Fight.IsSurging()?.28f:.57f;
   if(Fight.Move==EFightMove::Recover || Fight.Energy<.1f)ReelStart();else ReelStop();
   const float Lift=Fight.Move==EFightMove::Dive?25.f:Fight.Move==EFightMove::Jump?-25.f:0.f;
   PC->SetControlRotation(FRotator(HookFacingPitch+Lift,HookFacingYaw+Fight.RequiredSide()*30.f,0));
   if(PhaseTime>=.15f && PhaseTime<.5f)Screenshot(TEXT("Hook"));
   if(Fight.IsSurging() && Fight.MoveTime>=.45f)Screenshot(TEXT("Run"));
   if(Fight.Move==EFightMove::Recover && Fight.MoveTime>=.4f)Screenshot(TEXT("Recover"));
   if(Fight.Move==EFightMove::Jump && Fight.MoveTime>=1.f)Screenshot(TEXT("Jump"));
   if(Fight.Move==EFightMove::HeadShake && Fight.MoveTime>=1.f)Screenshot(TEXT("HeadShake"));
   break;
  }
  case EFishingPhase::Landing:
   ReelStop();PC->SetControlRotation(FRotator(HookFacingPitch,HookFacingYaw,0));
   if(PhaseTime>=.25f)Screenshot(TEXT("Landing"));
   if(PhaseTime>=.6f)Strike();
   break;
  case EFishingPhase::Landed:
   ReelStop();
   if(PhaseTime>=1.f)Screenshot(TEXT("Trophy"));
   if(PhaseTime>=4.f)Finish(State.bSawBite && State.bSawFight && State.Screenshots.Contains(TEXT("Trophy")),TEXT("natural bite, timed strike, adaptive fight and landing completed"));
   break;
 }
}

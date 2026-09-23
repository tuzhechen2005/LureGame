#include "LureWorld.h"
#include "LureSave.h"
#include "FishingVisuals.h"
#include "CoveTerrain.h"
#include "Camera/CameraComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"
#include "Sound/SoundBase.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "HAL/PlatformMisc.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

bool ALurePawn::HasFishingAssist() const {return SaveData && SaveData->bFishingAssist;}

void ALurePawn::InitializeShorePresentation(){
 auto Make=[&](const TCHAR* Name,const TCHAR* Path){
  auto* M=NewObject<UStaticMeshComponent>(this,Name);M->SetupAttachment(RootComponent);
  M->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Path));M->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  M->SetVisibility(false);M->RegisterComponent();return M;
 };
 CatchNet=Make(TEXT("LandingNet"),TEXT("/Game/Fishing/Shore/SM_LandingNet.SM_LandingNet"));
 auto* Material=LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/Fishing/Shore/M_SurfaceWake.M_SurfaceWake"));
 for(int32 Index=0;Index<5;++Index){
  auto* Cue=Make(*FString::Printf(TEXT("SurfaceCue%d"),Index),TEXT("/Game/LureArt/SM_Guide.SM_Guide"));
  Cue->SetCastShadow(false);if(Material)Cue->SetMaterial(0,Material);SurfaceCues.Add(Cue);
 }
}

float ALurePawn::RodLoad() const{
 if(Phase==EFishingPhase::Bite){
  const float Progress=BiteProgress();
  const float First=FMath::Exp(-FMath::Square((Progress-.17f)/.075f));
  const float Second=FMath::Exp(-FMath::Square((Progress-.44f)/.11f));
  return .12f+First*.65f+Second*.90f;
 }
 if(Phase==EFishingPhase::Fighting)return Tension+(Fight.Move==EFightMove::HeadShake?.07f*FMath::Sin(Clock*19.f):0.f);
 if(Phase==EFishingPhase::Retrieving)return (Reeling?.045f:.015f)+FMath::Max(0.f,1.f-(Clock-LastTwitch)*4.f)*.13f;
 return Phase==EFishingPhase::Landing?.24f:0.f;
}

FVector ALurePawn::RodBend() const{
 FVector Bend=-Camera->GetUpVector()*RodLoad()*42.f;
 if(Phase==EFishingPhase::Fighting){
  const FVector Pull=(LurePosition-GetActorLocation()).GetSafeNormal2D();
  const float Side=FVector::DotProduct(Pull,Camera->GetRightVector());
  Bend+=Camera->GetRightVector()*Side*FMath::Clamp(Tension,0.f,1.2f)*65.f;
 }
 return Bend;
}

void ALurePawn::SurfaceCue(FVector Position,float Strength){
 const bool Audible=Clock-CueTime>3.f || Strength>=.9f;
 CuePosition=Position;CuePosition.Z=.8f;CueTime=Clock;CueStrength=FMath::Clamp(Strength,.25f,1.f);
 // Volume tracks distance. These are small water sounds, separate from the
 // dry, close mechanical drag loop that signals load at the player's reel.
 const float Distance=FVector::Dist2D(GetActorLocation(),Position);
 if(auto* Sound=Audible?LoadObject<USoundBase>(nullptr,TEXT("/Game/Audio/Splash.Splash")):nullptr)
  UGameplayStatics::PlaySoundAtLocation(this,Sound,Position,Volume*.30f*CueStrength*FMath::Clamp(1.f-Distance/5500.f,.08f,1.f),1.25f);
}

void ALurePawn::UpdateShoreCues(float Dt){
 if(bMenuOpen)return;
 // Occasional surface feeding marks a real occupied habitat. It does not
 // create a follower or schedule a bite, and quiet/deep fish reveal nothing.
 if(Clock>=NextHabitatCue && (Phase==EFishingPhase::Ready || Phase==EFishingPhase::Retrieving)){
  NextHabitatCue=Clock+14.f+FMath::Fmod(float(PopulationSeed%101)+Clock,8.f);
  ALureFish* Nearby=nullptr;float Best=MAX_flt;
  for(auto* F:Fish){
   if(!IsValid(F)||F->Cooldown>0||F->Behavior!=EFishBehavior::Patrol||F->Home.Z<-135.f)continue;
   const float Distance=FVector::DistSquared2D(GetActorLocation(),F->GetActorLocation());
   if(Distance<Best){Best=Distance;Nearby=F;}
  }
  if(Nearby && Best<FMath::Square(3400.f)){
   Nearby->BeginSurfaceForage();
  }
 }
 if(Clock-CueTime>3.f)for(auto* F:Fish){
  if(IsValid(F) && F->IsSurfaceForaging() && F->GetActorLocation().Z>-20.f){SurfaceCue(F->GetActorLocation(),.45f);break;}
 }
 if(Phase==EFishingPhase::Fighting && ActiveFish && LurePosition.Z>-45.f && Clock-CueTime>.7f)
  SurfaceCue(LurePosition,Fight.Move==EFightMove::Recover?.3f:.85f);
 for(int32 Index=0;Index<SurfaceCues.Num();++Index){
  const float Age=Clock-CueTime-Index*.13f;
  const bool Visible=Age>=0.f && Age<1.5f && !bObserve;
  auto* Cue=SurfaceCues[Index];Cue->SetVisibility(Visible);
  if(!Visible)continue;
  const float Radius=(9.f+Age*72.f)*CueStrength;
  Cue->SetWorldLocation(CuePosition+FVector(Index*3.f,Index*-1.5f,Index*.06f));
  Cue->SetWorldRotation(FRotator(90,0,0));
  Cue->SetWorldScale3D(FVector(Radius,Radius*.62f,FMath::Max(.06f,(1.5f-Age)*.3f)));
 }
}

void ALurePawn::StartCatchPresentation(){
 if(!ActiveFish)return;
 CatchWaterPosition=LurePosition;CatchWaterPosition.Z=-8;
 const FRotator View=GetControlRotation();const FRotationMatrix Basis(View);
 const FVector Location=GetActorLocation()+FVector(0,0,170)+Basis.GetUnitAxis(EAxis::X)*135.f+
  Basis.GetUnitAxis(EAxis::Y)*32.f-Basis.GetUnitAxis(EAxis::Z)*20.f;
 const float Length=ActiveFish->Body->GetStaticMesh()?ActiveFish->Body->GetStaticMesh()->GetBoundingBox().GetSize().X*ActiveFish->SizeFactor+12:55.f;
 CatchDisplayTransform=FTransform(FRotator(0,View.Yaw+90.f,0),Location,FVector(FMath::Clamp(Length/64.f,.85f,1.7f)));
 UpdateCatchPresentation(0);
}

void ALurePawn::ReleaseOrResetCast(){
 if(bMenuOpen || Phase==EFishingPhase::Releasing)return;
 if(Phase!=EFishingPhase::Landed || !ActiveFish){ResetCast();return;}
 if(bObserve)ToggleObserve();
 SetPhase(EFishingPhase::Releasing);Reeling=false;EventLife=0;
}

void ALurePawn::UpdateCatchPresentation(float Dt){
 const bool Presented=ActiveFish && (Phase==EFishingPhase::Landed || Phase==EFishingPhase::Releasing);
 if(CatchNet)CatchNet->SetVisibility(Presented && !bMenuOpen);
 if(!Presented)return;
 const bool Releasing=Phase==EFishingPhase::Releasing;
 const float T=FMath::SmoothStep(0.f,1.f,FMath::Clamp(PhaseTime/(Releasing?1.65f:1.45f),0.f,1.f));
 FTransform Transform=CatchDisplayTransform;
 const FVector Water=CatchWaterPosition+FVector(0,0,12);
 Transform.SetLocation(FMath::Lerp(Water,CatchDisplayTransform.GetLocation(),Releasing?1.f-T:T));
 if(CatchNet){
  FTransform NetTransform=Transform;
  // FBX's converted handle extends along -Y; point it back to the angler.
  NetTransform.SetRotation(Transform.GetRotation()*FRotator(0,180,0).Quaternion());
  CatchNet->SetWorldTransform(NetTransform);
 }
 // The fish lies on its side inside the rubber basket, with its lowest body
 // surface touching the cupped mesh. Camera inspection never moves the prop.
 ActiveFish->Behavior=EFishBehavior::Hooked;
 ActiveFish->SetActorLocation(Transform.TransformPosition(FVector(0,0,-9.f)));
 const FQuat FishRotation=Transform.GetRotation()*FRotator(0,0,72.f+FMath::Sin(Clock*1.7f)*1.2f).Quaternion();
 ActiveFish->SetActorRotation(FishRotation);
 ActiveFish->Body->SetRelativeRotation(FRotator::ZeroRotator);
 ActiveFish->Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Clock*5)*3.f,0));
 if(Releasing && PhaseTime>=1.65f){
  const FVector At=CatchWaterPosition;SurfaceCue(At,.9f);ResetCast();
  Notice=TEXT("鱼已放流。换个落点，继续观察水面。");
 }
}

void ALurePawn::RunShoreTest(){
 int32 Errors=0;
 auto Check=[&](bool Good,const TCHAR* Label){UE_LOG(LogTemp,Display,TEXT("LURE_SHORE_TEST %s: %s"),Good?TEXT("PASS"):TEXT("FAIL"),Label);if(!Good)++Errors;};
 Check(CatchNet && CatchNet->GetStaticMesh(),TEXT("authored landing net is available at runtime"));
 Check(!HasFishingAssist(),TEXT("default shore mode does not expose fish state"));
 SetPhase(EFishingPhase::Retrieving);ToggleObserve();Check(!bObserve,TEXT("underwater camera is opt-in"));
 SaveData->bFishingAssist=true;ToggleObserve();Check(bObserve,TEXT("optional assist permits inspection"));
 ToggleObserve();SaveData->bFishingAssist=false;
 SetPhase(EFishingPhase::Bite);BiteWindow=1;PhaseTime=.17f;const float Tug=RodLoad();PhaseTime=.8f;
 Check(Tug>RodLoad()+.4f,TEXT("bite is readable as an actual rod-tip tug"));
 SurfaceCue(FVector(1500,0,-65),.7f);Clock+=.3f;UpdateShoreCues(.3f);
 Check(SurfaceCues.Num()==5 && SurfaceCues[0]->IsVisible() && SurfaceCues[0]->GetComponentLocation().Z>0,TEXT("surface cue renders at the water plane"));
 Check(Fish.Num()>=18,TEXT("shore session uses live habitat population"));
 ActiveFish=Fish.Num()>1?Fish[1]:nullptr;
 if(ActiveFish){
  Check(ActiveFish->Species==1 && ActiveFish->Body->GetStaticMesh() && ActiveFish->Body->GetStaticMesh()->GetName()==TEXT("SM_PerchNaturalBody"),TEXT("textured perch asset is available at runtime"));
  LurePosition=FVector(600,0,-12);SetPhase(EFishingPhase::Landed);StartCatchPresentation();PhaseTime=2;UpdateCatchPresentation(0);
  Check(CatchNet->IsVisible() && ActiveFish->GetActorLocation().Z<CatchNet->GetComponentLocation().Z,TEXT("landed fish rests inside the net, below its rim"));
  const FVector Before=ActiveFish->GetActorLocation();ToggleObserve();UpdateCatchPresentation(0);
  Check(bObserve && Before.Equals(ActiveFish->GetActorLocation(),.01),TEXT("inspection camera cannot move the supported catch"));
  const int32 BeforeCatches=Catches;auto* Released=ActiveFish;
  ReleaseOrResetCast();Check(Phase==EFishingPhase::Releasing && !bObserve,TEXT("release returns to first person and begins lowering the net"));
  PhaseTime=1.7f;UpdateCatchPresentation(0);
  Check(Phase==EFishingPhase::Ready && !ActiveFish && Released->Cooldown>=55 && Released->GetActorLocation().Z<0,TEXT("release returns fish underwater with recovery time"));
  Check(Catches==BeforeCatches && !CatchNet->IsVisible(),TEXT("release neither repeats catch rewards nor leaves floating props"));
 }
 UE_LOG(LogTemp,Display,TEXT("LURE_SHORE_TEST COMPLETE failures=%d"),Errors);
 FPlatformMisc::RequestExitWithStatus(false,Errors?1:0);
}

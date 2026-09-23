#include "FishingVisuals.h"
#include "CoveTerrain.h"
#include "Components/StaticMeshComponent.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
ALureFish::ALureFish(){
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 Body=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Bass"));Body->SetupAttachment(RootComponent);
 Body->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_BassBody_Refined.SM_BassBody_Refined")));
 Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Tail=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Tail"));Tail->SetupAttachment(Body);Tail->SetRelativeLocation(FVector(-22.5f,0,0));
 Tail->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_BassTail.SM_BassTail")));Tail->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void ALureFish::Initialize(FVector InHome,float Offset){
 Home=InHome;Seed=Offset;Age=Offset;
 HabitatIndex=-1;NoticeRadius=1800;TerritoryRadius=0;Wariness=0;
 EncounterCount=0;LastPopulationEncounter=0;
 ResetEncounter();
 SetActorLocation(Home);
 SetActorHiddenInGame(false);
}
void ALureFish::ConfigureHabitat(int32 Index,float InNoticeRadius,float InTerritoryRadius){
 HabitatIndex=FMath::Clamp(Index,0,2);
 NoticeRadius=FMath::Clamp(InNoticeRadius,650.f,1100.f);
 TerritoryRadius=FMath::Max(InTerritoryRadius,NoticeRadius);
}
bool ALureFish::CanRespondToLure(FVector Lure) const {
 if(Behavior==EFishBehavior::Hooked || Cooldown>0 || Lure.X<=50.f)return false;
 const float Radius=NoticeRadius*(1.f-.28f*Wariness);
 if(FVector::DistSquared(GetActorLocation(),Lure)>=FMath::Square(Radius))return false;
 // Deep residents must first see a presentation in their water column. A
 // follower may range within its patch, but cannot chase across the lake.
 if(HabitatIndex>=0 && (FMath::Abs(Lure.Z-Home.Z)>220.f ||
  FVector::DistSquared2D(Home,Lure)>FMath::Square(TerritoryRadius)))return false;
 return true;
}
bool ALureFish::BeginSurfaceForage(){
 if(HabitatIndex<0 || Behavior!=EFishBehavior::Patrol || Cooldown>0 || GetActorLocation().Z< -130.f)return false;
 SurfaceForageSeconds=6.f;SurfaceForageTarget=GetActorLocation();SurfaceForageTarget.Z=-10.f;return true;
}
void ALureFish::ResetEncounter(){
 SurfaceForageSeconds=0;
 Behavior=EFishBehavior::Patrol;
 InterestLevel=0;Curiosity=0;Cooldown=0;
 StrikeWindow=1;BiteStrength=1;
 RetrieveRunSeconds=0;PreviousPauseSeconds=0;PreviousRetrieveSpeed=0;
 PreviousTwitchAge=100;TwitchReactionCooldown=0;
 SameCadenceSeconds=0;CommitmentSeconds=0;bPauseRewarded=false;
}
bool ALureFish::Simulate(float Dt,FVector Lure,bool Attractive,const FLurePresentation& Presentation){
 if(Behavior==EFishBehavior::Hooked)return false;
 Dt=FMath::Max(0.f,Dt);
 SurfaceForageSeconds=FMath::Max(0.f,SurfaceForageSeconds-Dt);
 Age+=Dt;
 Cooldown=FMath::Max(0.f,Cooldown-Dt);
 Wariness=FMath::Max(0.f,Wariness-Dt/150.f);
 TwitchReactionCooldown=FMath::Max(0.f,TwitchReactionCooldown-Dt);
 CommitmentSeconds=FMath::Max(0.f,CommitmentSeconds-Dt);
 const FVector Pos=GetActorLocation();
 const float Distance=FVector::Distance(Pos,Lure);
 const float RetrieveSpeed=FMath::Max(0.f,Presentation.RetrieveSpeed);
 const float PauseSeconds=FMath::Max(0.f,Presentation.PauseSeconds);
 const float TwitchAge=FMath::Max(0.f,Presentation.TwitchAge);
 const bool Moving=RetrieveSpeed>=18.f;
 const bool WasMoving=PreviousRetrieveSpeed>=18.f;
 // A twitch is an edge, not a bonus applied every frame while its animation plays.
 const bool NewTwitch=TwitchAge<.28f &&
  (PreviousTwitchAge>=.28f || TwitchAge+.005f<PreviousTwitchAge);
 const bool Resumed=Moving && !WasMoving && PreviousPauseSeconds>=.35f && PreviousPauseSeconds<=3.5f;
 if(Moving){
  RetrieveRunSeconds=WasMoving?RetrieveRunSeconds+Dt:Dt;
 }else if(PauseSeconds>4.f){
  RetrieveRunSeconds=0;
 }
 const bool Paused=!Moving && !bPauseRewarded && RetrieveRunSeconds>=.55f &&
  PauseSeconds>=.32f && PauseSeconds<=2.4f;

 // Every lure works. These soft preferences reward readable choices without a
 // hidden combination lock. Depth is relative to the fish's original habitat.
 const int32 FishType=FMath::Clamp(Species,0,3);
 const int32 LureType=FMath::Clamp(Presentation.LureType,0,4);
 const float LureFits[4][5]={
  {1.f,1.f,.65f,1.f,.85f},
  {.75f,.85f,1.f,.45f,1.f},
  {1.f,.45f,1.f,.8f,.55f},
  {.9f,.55f,1.f,.6f,.85f}
 };
 const float PreferredSpeeds[]={155.f,115.f,205.f,185.f};
 const float LureFit=LureFits[FishType][LureType];
 const float DepthFit=1.f-FMath::Clamp(FMath::Abs(static_cast<float>(Lure.Z-Home.Z))/260.f,0.f,1.f);
 const float SpeedFit=1.f-FMath::Clamp(FMath::Abs(RetrieveSpeed-PreferredSpeeds[FishType])/190.f,0.f,1.f);
 const float Temperament=.5f+.5f*FMath::Sin(Seed*1.73f+FishType*.91f);
 const float Response=(.78f+.22f*LureFit+.18f*DepthFit+.08f*Temperament)*FMath::Clamp(Activity,.5f,1.6f)*(1.f-.35f*Wariness);

 FVector Target=Home+FVector(FMath::Sin(Age*.22f+Seed)*210,FMath::Cos(Age*.19f+Seed)*150,FMath::Sin(Age*.4f)*14);
 float Speed=55;
 const bool Engaged=Behavior==EFishBehavior::Following || Behavior==EFishBehavior::Hesitating || Behavior==EFishBehavior::Attacking;
 const bool CanNotice=Moving || TwitchAge<2.4f || (Engaged && InterestLevel>.04f);
 if(Attractive && CanRespondToLure(Lure) && CanNotice){
  SurfaceForageSeconds=0;
  if(Behavior!=EFishBehavior::Attacking){
   // Give a distant fish time to approach before judging the repeated cadence.
   SameCadenceSeconds=Distance<600.f?SameCadenceSeconds+Dt:0.f;
   float Cue=0;
   if(NewTwitch && TwitchReactionCooldown<=0 && PreviousTwitchAge+Dt>=.55f){
    Cue=.34f+.10f*LureFit+.08f*DepthFit;
    TwitchReactionCooldown=.7f;
   }
   if(Paused){
    Cue=FMath::Max(Cue,.30f+.10f*LureFit+.08f*DepthFit);
    bPauseRewarded=true;
   }
   if(Resumed && bPauseRewarded){
    Cue=FMath::Max(Cue,.20f+.06f*LureFit+.06f*DepthFit);
   }
   if(Cue>0){
    SameCadenceSeconds=0;
    // The fish must actually be close enough to read the presentation.
    if(Distance<600.f){
     InterestLevel=FMath::Min(1.f,InterestLevel+Cue);
     CommitmentSeconds=3.6f;
    }
   }
   const bool Bored=SameCadenceSeconds>5.5f || (!Moving && PauseSeconds>3.5f);
   if(Moving || (!Bored && CommitmentSeconds>0)){
    const float Proximity=Distance<450.f?1.f:.35f;
    // Identical retrieval can draw a follower but cannot cross the attack gate.
    const float InterestCap=CommitmentSeconds>0?1.f:(Bored?.48f:.66f);
    if(InterestLevel<InterestCap){
     InterestLevel=FMath::Min(InterestCap,InterestLevel+Dt*(.23f+.10f*SpeedFit)*Response*Proximity);
    }else if(CommitmentSeconds<=0){
     InterestLevel=FMath::Max(InterestCap,InterestLevel-Dt*.16f);
    }
   }else{
    InterestLevel=FMath::Max(0.f,InterestLevel-Dt*(Bored?.15f:.045f));
   }
   Behavior=Bored?EFishBehavior::Hesitating:EFishBehavior::Following;
   if(CommitmentSeconds>0 && InterestLevel>=.84f+.06f*Temperament+.06f*Wariness && Distance<310.f){
    Behavior=EFishBehavior::Attacking;
    const float SpeciesWindows[]={1.02f,1.10f,.88f,.90f};
    const float SpeciesStrengths[]={1.f,.78f,1.23f,1.04f};
    StrikeWindow=FMath::Clamp(SpeciesWindows[FishType]+.07f*LureFit+.08f*DepthFit-.06f*Temperament,.65f,1.15f);
    BiteStrength=FMath::Clamp(SpeciesStrengths[FishType]+.22f*(SizeFactor-1.f)+.10f*(Temperament-.5f),.6f,1.4f);
   }
  }
  const FVector Approach=(Lure-Pos).GetSafeNormal();
  const FVector Side(-Approach.Y,Approach.X,0);
  if(Behavior==EFishBehavior::Attacking){
   Target=Lure;
   Speed=430.f+100.f*BiteStrength;
  }else if(Behavior==EFishBehavior::Hesitating){
   Target=Lure-Approach*190.f+Side*(FMath::Sin(Age*1.7f+Seed)*90.f);
   Speed=FMath::Max(160.f,RetrieveSpeed+25.f);
  }else{
   Target=Lure-Approach*110.f+Side*(FMath::Sin(Age*1.2f+Seed)*32.f);
   Speed=FMath::Max(245.f+75.f*InterestLevel,RetrieveSpeed+65.f);
  }
 }else{
  InterestLevel=FMath::Max(0.f,InterestLevel-Dt*.30f);
  CommitmentSeconds=0;
  SameCadenceSeconds=0;
  Behavior=Cooldown>0?EFishBehavior::Escaping:EFishBehavior::Patrol;
  if(Cooldown>0)Speed=HabitatIndex<0 || FVector::DistSquared(Pos,Home)>FMath::Square(280.f)?190.f:35.f;
  if(!Attractive){RetrieveRunSeconds=0;bPauseRewarded=false;}
 }
 if(SurfaceForageSeconds>0 && Behavior==EFishBehavior::Patrol)Target=SurfaceForageTarget;
 if(Moving)bPauseRewarded=false;
 PreviousPauseSeconds=PauseSeconds;
 PreviousRetrieveSpeed=RetrieveSpeed;
 PreviousTwitchAge=TwitchAge;
 InterestLevel=FMath::Clamp(InterestLevel,0.f,1.f);
 Curiosity=InterestLevel;
 const FVector Direction=Target-Pos;
 if(!Direction.IsNearlyZero()){
  SetActorRotation(FMath::RInterpTo(GetActorRotation(),Direction.Rotation(),Dt,Behavior==EFishBehavior::Attacking?7.f:3.f));
  FVector Next=Pos+Direction.GetSafeNormal()*FMath::Min(static_cast<float>(Direction.Size()),Speed*Dt);
  if(HabitatIndex>=0){
   Next.X=FMath::Max(Next.X,static_cast<double>(Cove::ShoreX(Next.Y)+240.f));
   const double Upper=SurfaceForageSeconds>0?-10.0:FMath::Max(-24.0,Pos.Z-static_cast<double>(Dt*55.f));
   Next.Z=FMath::Clamp(Next.Z,static_cast<double>(Cove::Height(Next.X,Next.Y)+24.f),Upper);
  }
  SetActorLocation(Next);
 }
 Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Age*(Speed>100?15.f:7.f))*(bNaturalPerch?14.f:25.f),0));
 Body->SetRelativeRotation(FRotator(0,FMath::Sin(Age*7)*2,0));
 return Behavior==EFishBehavior::Attacking && FVector::DistSquared(GetActorLocation(),Lure)<FMath::Square(65.f);
}
void ALureFish::SetHooked(FVector MouthPosition,float Time){
 Behavior=EFishBehavior::Hooked;
 SetActorRotation(FRotator(0,180+FMath::Sin(Time*2)*22,FMath::Sin(Time*3)*9));
 SetActorLocation(MouthPosition-GetActorForwardVector()*20*SizeFactor);
 Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Time*20)*(bNaturalPerch?17.f:32.f),0));
}
void ALureFish::Escape(bool bReleased){
 ResetEncounter();Behavior=EFishBehavior::Escaping;++EncounterCount;
 const float Variation=.5f+.5f*FMath::Sin(Seed*2.13f+EncounterCount*1.17f);
 Cooldown=HabitatIndex<0?6.f:(bReleased?55.f+30.f*Variation:22.f+14.f*Variation);
 if(HabitatIndex>=0){
  Wariness=FMath::Min(1.f,Wariness+(bReleased?.8f:.55f));
  // Trophy display is above the bank: release back at the water's edge,
  // then let the fish swim home while its rest timer keeps it unavailable.
  FVector Release=GetActorLocation();
  Release.X=FMath::Max(Release.X,static_cast<double>(Cove::ShoreX(Release.Y)+240.f));
  Release.Z=FMath::Clamp(Release.Z,static_cast<double>(Cove::Height(Release.X,Release.Y)+24.f),-24.0);
  SetActorLocation(Release);
 }
 SetActorHiddenInGame(false);
}

void ALureFish::SetSpecies(int32 Type){
 Species=Type%4;
 const TCHAR* Paths[]={TEXT("/Game/LureArt/SM_BassBody_Refined.SM_BassBody_Refined"),TEXT("/Game/LureArt/SM_PerchBody_Refined.SM_PerchBody_Refined"),TEXT("/Game/LureArt/SM_PikeBody_Refined.SM_PikeBody_Refined"),TEXT("/Game/LureArt/SM_TroutBody_Refined.SM_TroutBody_Refined")};
 Body->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Paths[Species]));
 bNaturalPerch=false;
 Tail->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_BassTail.SM_BassTail")));
 if(Species==1){
  auto* NaturalBody=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Fishing/Perch/SM_PerchNaturalBody.SM_PerchNaturalBody"));
  auto* NaturalTail=LoadObject<UStaticMesh>(nullptr,TEXT("/Game/Fishing/Perch/SM_PerchNaturalTail.SM_PerchNaturalTail"));
  if(NaturalBody && NaturalTail){Body->SetStaticMesh(NaturalBody);Tail->SetStaticMesh(NaturalTail);bNaturalPerch=true;}
 }
 if(FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))){
  UE_LOG(LogTemp,Display,TEXT("LURE_FISH_ASSET species=%d mesh=%s"),Species,*GetPathNameSafe(Body->GetStaticMesh()));
 }
 SizeFactor=.8f+FMath::Frac(Seed*.719f+.31f)*.55f;
 const float Base[]={1.5f,.45f,3.2f,1.15f};Weight=Base[Species]*FMath::Pow(SizeFactor,3.f);
 SetActorScale3D(FVector(SizeFactor));
 const float TailX[]={-22.5f,-15.3f,-33.75f,-21.4f};Tail->SetRelativeLocation(FVector(TailX[Species],0,0));
 // Match the authored body proportions so changing species does not retain
 // a full-size bass tail on a smaller perch or narrower pike body.
 const FVector TailScale[]={FVector(1,1,1),FVector(.68f,.8f,1.08f),FVector(1.5f,.65f,.70f),FVector(.95f,.75f,.85f)};
 Tail->SetRelativeScale3D(TailScale[Species]);
 if(bNaturalPerch){Tail->SetRelativeLocation(FVector(-11.829231f,0,0));Tail->SetRelativeScale3D(FVector::OneVector);}
}
FString ALureFish::SpeciesName() const { const TCHAR* Names[]={TEXT("大口黑鲈"),TEXT("河鲈"),TEXT("白斑狗鱼"),TEXT("虹鳟")};return Names[Species];}

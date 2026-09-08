#include "FishingVisuals.h"
#include "Components/StaticMeshComponent.h"
ALureFish::ALureFish(){
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 Body=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Bass"));Body->SetupAttachment(RootComponent);
 Body->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_BassBody.SM_BassBody")));
 Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Tail=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Tail"));Tail->SetupAttachment(Body);Tail->SetRelativeLocation(FVector(-22.5f,0,0));
 Tail->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_BassTail.SM_BassTail")));Tail->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}
void ALureFish::Initialize(FVector InHome,float Offset){Home=InHome;Seed=Offset;Age=Offset;SetActorLocation(Home);}
bool ALureFish::Simulate(float Dt,FVector Lure,bool Attractive,bool Twitch){
 Age+=Dt;Cooldown=FMath::Max(0.f,Cooldown-Dt);
 const FVector Pos=GetActorLocation();const float Distance=FVector::Distance(Pos,Lure);
 FVector Target=Home+FVector(FMath::Sin(Age*.22f+Seed)*210,FMath::Cos(Age*.19f+Seed)*150,FMath::Sin(Age*.4f)*14);
 float Speed=55;
 if(Attractive && Cooldown<=0 && Distance<1800 && Lure.X>50){
  Behavior=EFishBehavior::Following;Target=Lure-FVector(25,0,0);Speed=260;
  if(Distance<260) Curiosity+=Dt*Activity*(Twitch?1.7f:.65f);
  if(Curiosity>1.1f){Behavior=EFishBehavior::Attacking;Speed=440;Target=Lure;}
 }else{Curiosity=FMath::Max(0.f,Curiosity-Dt);Behavior=Cooldown>0?EFishBehavior::Escaping:EFishBehavior::Patrol;if(Cooldown>0)Speed=190;}
 FVector Direction=Target-Pos;
 if(!Direction.IsNearlyZero()){
  SetActorRotation(FMath::RInterpTo(GetActorRotation(),Direction.Rotation(),Dt,3.f));
  SetActorLocation(Pos+Direction.GetSafeNormal()*FMath::Min(Direction.Size(),Speed*Dt));
 }
 Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Age*(Speed>100?15.f:7.f))*25,0));
 Body->SetRelativeRotation(FRotator(0,FMath::Sin(Age*7)*2,0));
 return Behavior==EFishBehavior::Attacking && Distance<65;
}
void ALureFish::SetHooked(FVector MouthPosition,float Time){
 Behavior=EFishBehavior::Hooked;
 SetActorRotation(FRotator(0,180+FMath::Sin(Time*2)*22,FMath::Sin(Time*3)*9));
 SetActorLocation(MouthPosition-GetActorForwardVector()*20*SizeFactor);
 Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Time*20)*32,0));
}
void ALureFish::Escape(){Behavior=EFishBehavior::Escaping;Cooldown=6;Curiosity=0;SetActorHiddenInGame(false);}

void ALureFish::SetSpecies(int32 Type){
 Species=Type%4;
 const TCHAR* Paths[]={TEXT("/Game/LureArt/SM_BassBody.SM_BassBody"),TEXT("/Game/LureArt/SM_PerchBody.SM_PerchBody"),TEXT("/Game/LureArt/SM_PikeBody.SM_PikeBody"),TEXT("/Game/LureArt/SM_TroutBody.SM_TroutBody")};
 Body->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Paths[Species]));
 SizeFactor=.8f+FMath::Frac(Seed*.719f+.31f)*.55f;
 const float Base[]={1.5f,.45f,3.2f,1.15f};Weight=Base[Species]*FMath::Pow(SizeFactor,3.f);
 SetActorScale3D(FVector(SizeFactor));
 const float TailX[]={-22.5f,-15.3f,-33.75f,-21.4f};Tail->SetRelativeLocation(FVector(TailX[Species],0,0));
}
FString ALureFish::SpeciesName() const { const TCHAR* Names[]={TEXT("大口黑鲈"),TEXT("河鲈"),TEXT("白斑狗鱼"),TEXT("虹鳟")};return Names[Species];}

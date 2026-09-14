#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FishingVisuals.generated.h"
class UStaticMeshComponent;
// RetrieveSpeed is deliberate horizontal retrieval, not passive sinking speed.
struct FLurePresentation {
 float RetrieveSpeed=0;
 float PauseSeconds=0;
 float TwitchAge=100;
 int32 LureType=0;
};
enum class EFishBehavior : uint8 { Patrol, Following, Attacking, Hooked, Escaping, Hesitating };
UCLASS()
class LUREGAME_API ALureFish : public AActor {
 GENERATED_BODY()
public:
 ALureFish();
 void Initialize(FVector InHome, float Offset);
 void ResetEncounter();
 bool Simulate(float Dt, FVector Lure, bool Attractive, const FLurePresentation& Presentation);
 void SetHooked(FVector MouthPosition, float Time);
 void Escape();
 EFishBehavior Behavior=EFishBehavior::Patrol;
 FVector Home;
 int32 Species=0;
 float SizeFactor=1,Weight=1,Activity=1;
 void SetSpecies(int32 Type);
 FString SpeciesName() const;
 float Curiosity=0, Cooldown=0;
 float InterestLevel=0, StrikeWindow=1, BiteStrength=1;
 UPROPERTY() UStaticMeshComponent* Body;
 UPROPERTY() UStaticMeshComponent* Tail;
private:
 float Age=0, Seed=0;
 float RetrieveRunSeconds=0, PreviousPauseSeconds=0, PreviousRetrieveSpeed=0;
 float PreviousTwitchAge=100, TwitchReactionCooldown=0;
 float SameCadenceSeconds=0, CommitmentSeconds=0;
 bool bPauseRewarded=false;
};

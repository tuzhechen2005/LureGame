#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FishingVisuals.generated.h"
class UStaticMeshComponent;
enum class EFishBehavior : uint8 { Patrol, Following, Attacking, Hooked, Escaping };
UCLASS()
class LUREGAME_API ALureFish : public AActor {
 GENERATED_BODY()
public:
 ALureFish();
 void Initialize(FVector InHome, float Offset);
 bool Simulate(float Dt, FVector Lure, bool Attractive, bool Twitch);
 void SetHooked(FVector MouthPosition, float Time);
 void Escape();
 EFishBehavior Behavior=EFishBehavior::Patrol;
 FVector Home;
 int32 Species=0;
 float SizeFactor=1,Weight=1,Activity=1;
 void SetSpecies(int32 Type);
 FString SpeciesName() const;
 float Curiosity=0, Cooldown=0;
 UPROPERTY() UStaticMeshComponent* Body;
 UPROPERTY() UStaticMeshComponent* Tail;
private:
 float Age=0, Seed=0;
};

#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CoveEnvironment.generated.h"
class UInstancedStaticMeshComponent;
class UStaticMeshComponent;
UCLASS()
class LUREGAME_API ACoveEnvironment : public AActor {
 GENERATED_BODY()
public:
 ACoveEnvironment();
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) UStaticMeshComponent* Terrain;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) UStaticMeshComponent* Water;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TArray<UInstancedStaticMeshComponent*> Groups;
};

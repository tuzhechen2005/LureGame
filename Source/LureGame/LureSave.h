#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "LureSave.generated.h"
USTRUCT()
struct FCatchRecord {
 GENERATED_BODY()
 UPROPERTY() FString Species;
 UPROPERTY() float Weight=0;
 UPROPERTY() float Length=0;
 UPROPERTY() FString Date;
 UPROPERTY() FString Lure;
};
UCLASS()
class LUREGAME_API ULureSave : public USaveGame {
 GENERATED_BODY()
public:
 UPROPERTY() TArray<FCatchRecord> Journal;
 UPROPERTY() float Sensitivity=.16f;
 UPROPERTY() float Volume=.65f;
 UPROPERTY() int32 Quality=2;
 UPROPERTY() int32 Weather=0;
 UPROPERTY() int32 TimeOfDay=0;
 UPROPERTY() int32 Spot=0;
 UPROPERTY() bool bFullscreen=false;
 UPROPERTY() int32 TotalCatches=0;
 UPROPERTY() float BestWeight=0;
};

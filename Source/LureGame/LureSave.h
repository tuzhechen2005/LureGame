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
 UPROPERTY() int32 Score=0;
 UPROPERTY() float HookQuality=0;
 UPROPERTY() float FightSeconds=0;
 UPROPERTY() int32 SpotId=-1;
 UPROPERTY() bool bTrophy=false;
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
 UPROPERTY() int32 Experience=0;
 UPROPERTY() TMap<FString,float> SpeciesBests;
 UPROPERTY() int32 CompletedMilestones=0;
 UPROPERTY() int32 CaughtSpots=0;
 UPROPERTY() int32 TrophyCatches=0;
};

#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "LureWorld.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class ALureFish;
class ULureSave;
class UAudioComponent;
class UFont;
enum class EFishingPhase : uint8 { Ready, Charging, Flying, Retrieving, Bite, Fighting, Landed };

UCLASS()
class LUREGAME_API ALurePawn : public APawn {
 GENERATED_BODY()
public:
 ALurePawn();
 virtual void BeginPlay() override;
 virtual void Tick(float DeltaSeconds) override;
 virtual void SetupPlayerInputComponent(UInputComponent* Input) override;
 EFishingPhase Phase = EFishingPhase::Ready;
 float Charge=0, Tension=0, Stamina=1, Depth=0, Drag=0.55f;
 int32 Catches=0, LureType=0;
 FString Notice;
 FVector LurePosition=FVector::ZeroVector;
 float DistanceMetres() const;
 bool bObserve=false;
 FString FishStatus() const;
 bool bMenuOpen=false,bStarted=false;
 int32 MenuPage=0,Weather=0,TimeOfDay=0,Spot=0;
 float Sensitivity=.16f,Volume=.65f;
 FString LastCatch;
 UPROPERTY() ULureSave* SaveData;
 void SessionInit();
 void SaveSession();
 void MenuAction(const FString& Action);
 void ApplyEnvironment();
 void UpdateEnvironment(float Dt);
 void RecordCatch();
 void PlayCue(const TCHAR* Name);
 FString LureName() const;
 FString WeatherName() const;
 FString TimeName() const;
 FString SpotName() const;
 void RunSessionTest();

private:
 UPROPERTY() UCameraComponent* Camera;
 UPROPERTY() UAudioComponent* AmbientAudio;
 UPROPERTY() UAudioComponent* ReelAudio;
 UPROPERTY() class UInstancedStaticMeshComponent* Rain;

 UPROPERTY() UStaticMeshComponent* Rod;
 UPROPERTY() UStaticMeshComponent* Lure;
 UPROPERTY() USceneComponent* Rig;
 UPROPERTY() UStaticMeshComponent* RightArm;
 UPROPERTY() UStaticMeshComponent* LeftArm;
 UPROPERTY() UStaticMeshComponent* Crank;
 UPROPERTY() TArray<UStaticMeshComponent*> Blank;
 UPROPERTY() TArray<UStaticMeshComponent*> Guides;
 UPROPERTY() TArray<UStaticMeshComponent*> Line;
 UPROPERTY() TArray<UStaticMeshComponent*> Ripples;
 UPROPERTY() TArray<ALureFish*> Fish;
 UPROPERTY() ALureFish* ActiveFish=nullptr;
 FVector SplashPosition=FVector::ZeroVector;
 float SplashTime=-10, CrankAngle=0;
 void UpdateRig(float Dt);
 void UpdateFish(float Dt);
 void ToggleObserve();
 void CaptureMouse();
 void ReleaseMouse();
 void RunInputTest();
 FVector Velocity=FVector::ZeroVector;
 float FrameDelta=1.f/60.f;
 float PhaseTime=0, Interest=0, LastTwitch=-10, Clock=0;
 bool Reeling=false;
 void MoveForward(float V);
 void MoveRight(float V);
 void LookYaw(float V);
 void LookPitch(float V);
 void PressCast();
 void ReleaseCast();
 void ReelStart();
 void ReelStop();
 void Strike();
 void ResetCast();
 void SwitchLure();
 void DragUp();
 void DragDown();
 void SetPhase(EFishingPhase Next);
 void RunSmokeTest();
};

UCLASS()
class LUREGAME_API ALureHUD : public AHUD {
 GENERATED_BODY()
public:
 virtual void DrawHUD() override;
private:
 UPROPERTY() UFont* ChineseFont;
};

UCLASS()
class LUREGAME_API ALureGameMode : public AGameModeBase {
 GENERATED_BODY()
public:
 ALureGameMode();
 virtual void BeginPlay() override;
};




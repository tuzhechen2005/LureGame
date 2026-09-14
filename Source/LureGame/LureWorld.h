#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Pawn.h"
#include "GameFramework/GameModeBase.h"
#include "GameFramework/HUD.h"
#include "FishingEncounter.h"
#include "LureWorld.generated.h"

class UCameraComponent;
class UStaticMeshComponent;
class USkeletalMeshComponent;
class ALureFish;
class ULureSave;
class UAudioComponent;
class UFont;
enum class EFishingPhase : uint8 { Ready, Charging, Flying, Retrieving, Bite, Fighting, Landed, Landing };

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
 FFishingFight Fight;
 float BiteWindow=1.f,HookQuality=0,EventLife=0,EventDuration=1;
 FString EventTitle,EventDetail,CatchGrade;
 int32 CatchScore=0,CatchXP=0;
 bool bPersonalBest=false,bNewSpecies=false;
 float BiteProgress() const { return Phase==EFishingPhase::Bite?FMath::Clamp(PhaseTime/BiteWindow,0.f,1.f):0.f; }
 float LandingProgress() const { return Phase==EFishingPhase::Landing?FMath::Clamp(PhaseTime/4.f,0.f,1.f):0.f; }
 FString CadenceHint() const;
 FString ProgressTitle() const;
 FString ProgressDetail() const;
 float ProgressFraction() const;
 FString RankName() const;
 float RankProgress() const;
 FString HabitatHint() const;
 static float TrophyThreshold(int32 Species);
 FString MilestoneText;
 int32 MilestoneXP=0;
 bool bTrophy=false;
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
 UPROPERTY() UAudioComponent* DragAudio;
 UPROPERTY() class UInstancedStaticMeshComponent* Rain;

 UPROPERTY() UStaticMeshComponent* Rod;
 UPROPERTY() UStaticMeshComponent* Lure;
 UPROPERTY() USceneComponent* Rig;
 UPROPERTY() UStaticMeshComponent* RightArm;
 UPROPERTY() UStaticMeshComponent* LeftArm;
 UPROPERTY() UStaticMeshComponent* Crank;
 UPROPERTY() USkeletalMeshComponent* AuthoredRig;
 bool bUseAuthoredRig=false;
 void InitializeAuthoredRig();
 FVector RodTip() const;
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
 float LastReelStop=-10,LastFollowCue=-10,Impact=0,HookFacingYaw=0,HookFacingPitch=0;
 float LastCastQuality=0;
 float RodSideInput=0,RodLiftInput=0;
 FVector FightBearing=FVector::ForwardVector;
 void Announce(const FString& Title,const FString& Detail,float Seconds,float Punch=0);
 void StartFight();
 void EndFight(bool bSuccess,const FString& Reason);
 void TickEncounter(float Dt);
 void RunEncounterTest();
 void RunEncounterCapture(float Dt);
 void UpdateProgression();
 void RunProgressionTest();
 void PopulateLake();
 void ReplenishFish(ALureFish* Released);
 void RunPopulationTest();
 int32 PopulationSeed=0,PopulationGeneration=0;
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




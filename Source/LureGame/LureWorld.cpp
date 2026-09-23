#include "LureWorld.h"
#include "CoveEnvironment.h"
#include "CoveTerrain.h"
#include "Kismet/GameplayStatics.h"
#include "FishingVisuals.h"
#include "LureSave.h"
#include "Engine/GameViewportClient.h"
#include "GameFramework/PlayerInput.h"
#include "InputKeyEventArgs.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Engine/ExponentialHeightFog.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "Camera/CameraComponent.h"
#include "Camera/PlayerCameraManager.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "Engine/SkeletalMesh.h"
#include "Components/InputComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/World.h"
#include "Engine/Canvas.h"
#include "UnrealClient.h"
#include "Engine/Engine.h"
#include "GameFramework/PlayerController.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "DrawDebugHelpers.h"
#include "InputCoreTypes.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformMemory.h"

namespace {
UStaticMesh* Shape(const TCHAR* Name) {
 return LoadObject<UStaticMesh>(nullptr, *FString::Printf(TEXT("/Engine/BasicShapes/%s.%s"),Name,Name));
}
void Tint(UStaticMeshComponent* Mesh, FLinearColor Color) {
 UMaterialInterface* Base=LoadObject<UMaterialInterface>(nullptr,TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
 if(Base) { auto* Mat=UMaterialInstanceDynamic::Create(Base,Mesh); Mat->SetVectorParameterValue(TEXT("Color"),Color); Mesh->SetMaterial(0,Mat); }
}
AStaticMeshActor* Place(UWorld* World,const TCHAR* Mesh,FVector Position,FVector Scale,FLinearColor Color) {
 auto* A=World->SpawnActor<AStaticMeshActor>(Position,FRotator::ZeroRotator);
 A->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
 A->GetStaticMeshComponent()->SetStaticMesh(Shape(Mesh));
 A->SetActorScale3D(Scale); Tint(A->GetStaticMeshComponent(),Color); return A;
}
}
ALurePawn::ALurePawn() {
 PrimaryActorTick.bCanEverTick=true;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 Camera=CreateDefaultSubobject<UCameraComponent>(TEXT("View")); Camera->SetupAttachment(RootComponent);
 Camera->SetFieldOfView(80); Camera->SetRelativeLocation(FVector(0,0,170)); Camera->bUsePawnControlRotation=true;
 Rig=CreateDefaultSubobject<USceneComponent>(TEXT("FishingRig")); Rig->SetupAttachment(Camera);
 Rig->SetRelativeLocation(FVector(65,22,-20)); Rig->SetRelativeRotation(FRotator(12,-10,0));
 AuthoredRig=CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("AuthoredFishingRig"));
 AuthoredRig->SetupAttachment(Rig);AuthoredRig->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 AuthoredRig->SetVisibility(false);AuthoredRig->SetCastShadow(false);
 AuthoredRig->VisibilityBasedAnimTickOption=EVisibilityBasedAnimTickOption::AlwaysTickPoseAndRefreshBones;
 auto Make=[&](const FString& Name,const TCHAR* Asset,USceneComponent* Parent){
  auto* M=CreateDefaultSubobject<UStaticMeshComponent>(*Name);M->SetupAttachment(Parent);
  M->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Asset));M->SetCollisionEnabled(ECollisionEnabled::NoCollision);return M;
 };
 Rod=Make(TEXT("RodHandle"),TEXT("/Game/LureArt/SM_RodHandle.SM_RodHandle"),Rig);
 RightArm=Make(TEXT("RightArm"),TEXT("/Game/LureArt/SM_AnatomicalLeft.SM_AnatomicalLeft"),Rig);
 LeftArm=Make(TEXT("LeftArm"),TEXT("/Game/LureArt/SM_AnatomicalRight.SM_AnatomicalRight"),Rig);
 LeftArm->SetRelativeLocation(FVector(-1,-7,-8));LeftArm->SetRelativeRotation(FRotator::ZeroRotator);
 Crank=Make(TEXT("ReelCrank"),TEXT("/Game/LureArt/SM_ReelCrank_Transverse.SM_ReelCrank_Transverse"),Rig);Crank->SetRelativeLocation(FVector(-1,-2.8f,-7.5f));Crank->SetRelativeScale3D(FVector::OneVector);
 for(int i=0;i<16;++i){Blank.Add(Make(FString::Printf(TEXT("Blank%d"),i),TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),Rig));}
 for(int i=0;i<7;++i){Guides.Add(Make(FString::Printf(TEXT("Guide%d"),i),TEXT("/Game/LureArt/SM_Guide.SM_Guide"),Rig));}
 for(int i=0;i<24;++i){Line.Add(Make(FString::Printf(TEXT("Line%d"),i),TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),RootComponent));}
 for(int i=0;i<3;++i){Ripples.Add(Make(FString::Printf(TEXT("Ripple%d"),i),TEXT("/Game/LureArt/SM_Guide.SM_Guide"),RootComponent));}
 Lure=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Lure")); Lure->SetupAttachment(RootComponent);
 Lure->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Minnow.SM_Minnow"))); Lure->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 AutoPossessPlayer=EAutoReceiveInput::Player0;
}
void ALurePawn::BeginPlay() {
 Super::BeginPlay(); SetActorLocation(FVector(-550,0,70));
 for(auto* B:Blank) Tint(B,FLinearColor(.015f,.021f,.024f));
 for(auto* L:Line) Tint(L,FLinearColor(.4f,.48f,.42f));
 if(auto* PC=Cast<APlayerController>(GetController())) { PC->SetControlRotation(FRotator(-7,-40,0)); PC->PlayerCameraManager->ViewPitchMin=-75;PC->PlayerCameraManager->ViewPitchMax=70; }
 CaptureMouse();
 PopulateLake();
 ResetCast();
 SessionInit();
 InitializeAuthoredRig();
 InitializeShorePresentation();
 if(FParse::Param(FCommandLine::Get(),TEXT("LurePopulationTest"))) RunPopulationTest();
 if(FParse::Param(FCommandLine::Get(),TEXT("LureEncounterTest"))) RunEncounterTest();
 if(FParse::Param(FCommandLine::Get(),TEXT("LureSmokeTest"))) RunSmokeTest();
}
void ALurePawn::SetupPlayerInputComponent(UInputComponent* I) {
 Super::SetupPlayerInputComponent(I);


 I->BindAxisKey(EKeys::MouseX,this,&ALurePawn::LookYaw); I->BindAxisKey(EKeys::MouseY,this,&ALurePawn::LookPitch);
 I->BindKey(EKeys::LeftMouseButton,IE_Pressed,this,&ALurePawn::PressCast); I->BindKey(EKeys::LeftMouseButton,IE_Released,this,&ALurePawn::ReleaseCast);
 I->BindKey(EKeys::RightMouseButton,IE_Pressed,this,&ALurePawn::ReelStart); I->BindKey(EKeys::RightMouseButton,IE_Released,this,&ALurePawn::ReelStop);
 I->BindKey(EKeys::SpaceBar,IE_Pressed,this,&ALurePawn::Strike); I->BindKey(EKeys::R,IE_Pressed,this,&ALurePawn::ReleaseOrResetCast);
 I->BindKey(EKeys::Tab,IE_Pressed,this,&ALurePawn::SwitchLure);
 I->BindKey(EKeys::V,IE_Pressed,this,&ALurePawn::ToggleObserve);
 I->BindKey(EKeys::Escape,IE_Pressed,this,&ALurePawn::ReleaseMouse);
 I->BindKey(EKeys::MouseScrollUp,IE_Pressed,this,&ALurePawn::DragUp); I->BindKey(EKeys::MouseScrollDown,IE_Pressed,this,&ALurePawn::DragDown);
}
void ALurePawn::MoveForward(float V) {
 if(Phase==EFishingPhase::Releasing || (Phase==EFishingPhase::Landed && ActiveFish))return;
 if(V==0 || bObserve || Phase==EFishingPhase::Fighting || Phase==EFishingPhase::Landing) return;
 
 FVector P=GetActorLocation()+FRotator(0,GetControlRotation().Yaw,0).Vector()*V*220*FrameDelta;
 P.X=FMath::Clamp(P.X,-1300.0f,-240.0f); P.Y=FMath::Clamp(P.Y,-1900.0f,1900.0f); P.Z=Cove::Height(P.X,P.Y); SetActorLocation(P);
}
void ALurePawn::MoveRight(float V) {
 if(Phase==EFishingPhase::Releasing || (Phase==EFishingPhase::Landed && ActiveFish))return;
 if(V==0 || bObserve || Phase==EFishingPhase::Fighting || Phase==EFishingPhase::Landing) return;
 
 FVector P=GetActorLocation()+FRotationMatrix(FRotator(0,GetControlRotation().Yaw,0)).GetUnitAxis(EAxis::Y)*V*220*FrameDelta;
 P.X=FMath::Clamp(P.X,-1300.0f,-240.0f); P.Y=FMath::Clamp(P.Y,-1900.0f,1900.0f); P.Z=Cove::Height(P.X,P.Y); SetActorLocation(P);
}
void ALurePawn::LookYaw(float V) { if(!bObserve && !bMenuOpen) AddControllerYawInput(V*Sensitivity); }
void ALurePawn::LookPitch(float V) { if(!bObserve && !bMenuOpen) AddControllerPitchInput(-V*Sensitivity); }
void ALurePawn::SetPhase(EFishingPhase N) { Phase=N; PhaseTime=0; }
void ALurePawn::PressCast() { if(bMenuOpen)return; CaptureMouse(); if(Phase==EFishingPhase::Ready) {Charge=0; SetPhase(EFishingPhase::Charging);} }
void ALurePawn::ReleaseCast() {
 if(Phase!=EFishingPhase::Charging) return;
 FRotator Aim=GetControlRotation(); Aim.Pitch=FMath::Clamp(Aim.Pitch+22.f,10.f,65.f);
 LurePosition=Camera->GetComponentLocation()+Camera->GetForwardVector()*120;
 Velocity=Aim.Vector()*FMath::Lerp(1100.f,3200.f,Charge); SetPhase(EFishingPhase::Flying); PlayCue(TEXT("Cast")); Charge=0; Notice=TEXT("拟饵已抛出");
}
void ALurePawn::ReelStart(){if(!bMenuOpen)Reeling=true;}
void ALurePawn::ReelStop(){if(Reeling)LastReelStop=Clock;Reeling=false;}
void ALurePawn::Strike() {
 if(bMenuOpen)return;
 if(Phase==EFishingPhase::Bite && ActiveFish) StartFight();
 else if(Phase==EFishingPhase::Landing && ActiveFish) EndFight(true,TEXT(""));
 else if(Phase==EFishingPhase::Retrieving && Clock-LastTwitch>.45f) {LastTwitch=Clock;Impact=.12f; Notice=TEXT("轻抽一下，停顿，等待拟饵下沉。");}
}
void ALurePawn::ResetCast(){
 if(ActiveFish){
  const bool Released=Phase==EFishingPhase::Landed || Phase==EFishingPhase::Releasing;
  if(Released)ActiveFish->SetActorLocation(CatchWaterPosition+FVector(0,0,-30));
  ActiveFish->Escape(Released);ReplenishFish(ActiveFish);ActiveFish=nullptr;
 }
 if(bObserve)ToggleObserve();
 if(CatchNet)CatchNet->SetVisibility(false);
 SetPhase(EFishingPhase::Ready);Charge=0;Tension=0;Interest=0;Reeling=false;Depth=0;
 RodSideInput=RodLiftInput=0;LastReelStop=Clock;LastTwitch=Clock-10;EventLife=0;
 Notice=TEXT("向湖面瞄准，按住左键蓄力，松开抛投。");
}
void ALurePawn::SwitchLure(){ if(Phase==EFishingPhase::Ready && !bMenuOpen){LureType=(LureType+1)%5;
 const TCHAR* Names[]={TEXT("SM_Minnow"),TEXT("SM_SoftBait"),TEXT("SM_Spinner"),TEXT("SM_Popper"),TEXT("SM_Jig")};
 Lure->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/LureArt/%s.%s"),Names[LureType],Names[LureType])));Notice=LureName();} }
void ALurePawn::DragUp(){Drag=FMath::Clamp(Drag+0.05f,0.1f,1.f);}
void ALurePawn::DragDown(){Drag=FMath::Clamp(Drag-0.05f,0.1f,1.f);}
float ALurePawn::DistanceMetres() const {return FVector::Dist2D(GetActorLocation(),LurePosition)/100.f;}
void ALurePawn::Tick(float Dt) {
 Super::Tick(Dt); FrameDelta=Dt;
 if(!bMenuOpen || FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture")))Clock+=Dt;
 UpdateEnvironment(Dt);
 if(FParse::Param(FCommandLine::Get(),TEXT("LureSessionTest")) && Clock>1 && Clock-Dt<=1)RunSessionTest();
 if(FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"))){
  auto At=[&](float T){return Clock>T && Clock-Dt<=T;};
  if(At(10))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Menu.png"),true,false);
  if(At(11))MenuPage=1;
  if(At(13))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Settings.png"),true,false);
  if(Clock>15)FPlatformMisc::RequestExit(false);
 }
 if(bMenuOpen){Reeling=false;for(auto* L:Line)L->SetVisibility(false);return;}
 if(FParse::Param(FCommandLine::Get(),TEXT("LureRigReview"))){
  auto At=[&](float T){return Clock>T && Clock-Dt<=T;};
  if(At(12)) FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/AuthoredRig-Ready.png"),true,false);
  if(At(13))ReelStart();
  if(At(13.3f))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/AuthoredRig-ReelA.png"),true,false);
  if(At(13.6f))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/AuthoredRig-ReelB.png"),true,false);
  if(Clock>15)FPlatformMisc::RequestExit(false);
 }
 PhaseTime+=Dt;
 if(FParse::Param(FCommandLine::Get(),TEXT("LureEncounterCapture")))RunEncounterCapture(Dt);
 if(FParse::Param(FCommandLine::Get(),TEXT("LureShoreCapture")))RunShoreCapture(Dt);
 if(FParse::Param(FCommandLine::Get(),TEXT("LureShoreTest")) && Clock>1 && Clock-Dt<=1)RunShoreTest();
 if(FParse::Param(FCommandLine::Get(),TEXT("LureInputTest")) && Clock>1 && Clock-Dt<=1) RunInputTest();
 if(auto* PC=Cast<APlayerController>(GetController())) { MoveForward(float(PC->IsInputKeyDown(EKeys::W))-float(PC->IsInputKeyDown(EKeys::S))); MoveRight(float(PC->IsInputKeyDown(EKeys::D))-float(PC->IsInputKeyDown(EKeys::A))); }
 if(FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))) {
  static TArray<float> FrameSamples;if(Clock>10)FrameSamples.Add(Dt);
  auto At=[&](float T){return Clock>T && Clock-Dt<=T;};
  if(At(20))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Prototype.png"),true,false);
  if(At(21))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/WaterMotion.png"),true,false);
  if(At(22))PressCast();
  if(At(23))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Casting.png"),true,false);
  if(At(23.5f))ReleaseCast();
  if(At(28) && !bObserve)ToggleObserve();
  // The visual capture must frame an actual fish even when no natural bite
  // occurs before the scheduled shot. This setup is capture-only.
  if(At(33) && !ActiveFish && Fish.Num()>0){
   LurePosition=FVector(2000,0,-180);ActiveFish=Fish[0];
   SetPhase(EFishingPhase::Bite);Strike();
   UE_LOG(LogTemp,Display,TEXT("LURE_CAPTURE: staged fish close-up; not natural-bite evidence"));
  }
  if(Phase==EFishingPhase::Bite)Strike();
  if(At(35))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Fish.png"),true,false);
  if(At(36))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/FishMotion.png"),true,false);
  if(At(37)){if(bObserve)ToggleObserve();ReelStart();Drag=.45f;}
  if(At(40))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Fighting.png"),true,false);
  if(At(44)){ResetCast();Weather=3;ApplyEnvironment();}
  if(At(49))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Rain.png"),true,false);
  if(At(50)){Weather=0;TimeOfDay=2;ApplyEnvironment();}
  if(At(55))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Sunset.png"),true,false);
  if(At(56)){TimeOfDay=3;ApplyEnvironment();}
  if(At(61))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Night.png"),true,false);
  if(Clock>64){float Sum=0;for(float V:FrameSamples)Sum+=V;FrameSamples.Sort();int Count=FrameSamples.Num();if(Count)UE_LOG(LogTemp,Display,TEXT("LURE_PERF frames=%d avg_ms=%.2f p95_ms=%.2f working_set_mb=%.0f offscreen_capture=true"),Count,Sum/Count*1000,FrameSamples[FMath::Min(Count-1,int(Count*.95f))]*1000,FPlatformMemory::GetStats().UsedPhysical/1048576.0);FPlatformMisc::RequestExit(false);}
 }
 UpdateRig(Dt);
 const FVector Tip=RodTip();
 if(Phase==EFishingPhase::Ready || Phase==EFishingPhase::Charging) {
  LurePosition=Tip-FVector(0,0,60); if(Phase==EFishingPhase::Charging) Charge=FMath::Min(PhaseTime/1.5f,1.f);
 } else if(Phase==EFishingPhase::Flying) {
  Velocity.Z-=980*Dt; LurePosition+=Velocity*Dt;
  if(LurePosition.Z<=0) {
   if(LurePosition.X<0 || LurePosition.X>7000 || FMath::Abs(LurePosition.Y)>4000){ResetCast(); Notice=TEXT("落点在岸上，请朝开阔水面抛投。");}
   else {LurePosition.Z=0; SplashPosition=LurePosition;SplashTime=Clock;LastReelStop=Clock;PlayCue(TEXT("Splash")); SetPhase(EFishingPhase::Retrieving); Notice=TEXT("拟饵入水。右键收线，空格轻抽。");}
  }
 } else if(Phase==EFishingPhase::Retrieving || Phase==EFishingPhase::Bite) {
  FVector Toward=GetActorLocation()-LurePosition; Toward.Z=0;
  const float Speeds[]={180.f,120.f,220.f,110.f,100.f};
  if(Reeling) LurePosition+=Toward.GetSafeNormal()*Speeds[LureType]*Dt;
  if(LureType==0)LurePosition.Z=FMath::FInterpTo(LurePosition.Z,Reeling?-80.f:-25.f,Dt,1.5f);
  else if(LureType==3)LurePosition.Z=2+FMath::Sin(Clock*3)*1.5f;
  else {float Sink=LureType==4?75.f:(LureType==1?35.f:45.f);LurePosition.Z=FMath::Clamp(LurePosition.Z+Dt*(Reeling?30.f:-Sink),-340.f,-8.f);}
  Depth=FMath::Max(0.f,-LurePosition.Z/100);
  if(Clock-LastTwitch<0.3f) LurePosition.Z+=50*Dt;
  if(DistanceMetres()<3 || LurePosition.X<50){ResetCast(); Notice=TEXT("拟饵已收回，可以再次抛投。");}
  else if(Phase==EFishingPhase::Bite && PhaseTime>BiteWindow){if(ActiveFish){ActiveFish->Escape();ReplenishFish(ActiveFish);}ActiveFish=nullptr;SetPhase(EFishingPhase::Retrieving);PlayCue(TEXT("Escape"));Announce(TEXT("竿尖的拉力消失了"),HasFishingAssist()?TEXT("下次留意竿尖，在咬口亮区按空格"):TEXT("继续收停，或换个落点再试试"),2.5f);Notice=TEXT("错过咬口，换个节奏再试试。");}
 }
 TickEncounter(Dt);
 UpdateFish(Dt);
 UpdateCatchPresentation(Dt);
 UpdateShoreCues(Dt);
 Lure->SetVisibility(Phase!=EFishingPhase::Landed && Phase!=EFishingPhase::Releasing);
 Lure->SetWorldLocation(LurePosition);
 Lure->SetWorldRotation((GetActorLocation()-LurePosition).Rotation());
 if(bObserve && ActiveFish){
  FVector Focus=ActiveFish->GetActorLocation();FVector Eye;
  if(Phase==EFishingPhase::Landed){
   Eye=Focus+CatchDisplayTransform.TransformVectorNoScale(FVector(0,58,58));
   Focus-=CatchDisplayTransform.TransformVectorNoScale(FVector(12,0,0));
  }else{Eye=Focus+FVector(-90,145,55);Eye.Z=FMath::Min(Focus.Z+25,-30.f);}
  Camera->SetWorldLocation(Eye);Camera->SetWorldRotation((Focus-Eye).Rotation());
 }else if(bObserve){FVector Eye=LurePosition+FVector(-120,-180,45);Camera->SetWorldLocation(Eye);Camera->SetWorldRotation((LurePosition-Eye).Rotation());}
 for(int i=0;i<Line.Num();++i){
  float A=float(i)/Line.Num(),B=float(i+1)/Line.Num();
  auto Point=[&](float T){return FMath::Lerp(Tip,LurePosition,T)-FVector(0,0,FMath::Sin(T*PI)*(Phase==EFishingPhase::Fighting?8:35));};
  FVector P=Point(A),Q=Point(B),D=Q-P;
  Line[i]->SetWorldLocation((P+Q)*.5f);Line[i]->SetWorldRotation(FRotationMatrix::MakeFromZ(D).Rotator());
  Line[i]->SetWorldScale3D(FVector(.0012f,.0012f,D.Size()/100));Line[i]->SetVisibility(Phase!=EFishingPhase::Landed && Phase!=EFishingPhase::Releasing);
 }
 for(int i=0;i<Ripples.Num();++i){
  const float Age=Clock-SplashTime-i*.15f;float Radius=8+Age*75;
  Ripples[i]->SetVisibility(Age>=0 && Age<1.8f);Ripples[i]->SetWorldLocation(SplashPosition+FVector(0,0,3+i*.15f));
  Ripples[i]->SetWorldRotation(FRotator(90,0,0));Ripples[i]->SetWorldScale3D(FVector(Radius,Radius,Radius*.07f));
 }
}
void ALurePawn::CaptureMouse(){
 if(auto* PC=Cast<APlayerController>(GetController())){
  FInputModeGameOnly Mode;Mode.SetConsumeCaptureMouseDown(false);PC->SetInputMode(Mode);PC->bShowMouseCursor=false;
  if(auto* VP=GetWorld()->GetGameViewport()){VP->SetMouseCaptureMode(EMouseCaptureMode::CapturePermanently_IncludingInitialMouseDown);VP->SetMouseLockMode(EMouseLockMode::LockAlways);}
 }
}
void ALurePawn::ReleaseMouse(){
 if(bMenuOpen){if(bStarted)MenuAction(TEXT("play"));return;}
 if(Phase==EFishingPhase::Charging)ResetCast();
 bMenuOpen=true;MenuPage=0;Reeling=false;Rig->SetVisibility(false,true);SaveSession();
 if(auto* PC=Cast<APlayerController>(GetController())){PC->SetInputMode(FInputModeGameAndUI());PC->bShowMouseCursor=true;}
}
void ALurePawn::ToggleObserve(){
 if(!bObserve && (Phase==EFishingPhase::Releasing || bMenuOpen))return;
 if(!bObserve && Phase!=EFishingPhase::Landed && !HasFishingAssist()){
  Notice=TEXT("岸钓模式：留意竿线。Esc → 设置可开启水下观察辅助。");return;
 }
 if(!bObserve && (Phase==EFishingPhase::Ready || Phase==EFishingPhase::Charging || Phase==EFishingPhase::Flying))return;
 bObserve=!bObserve;Camera->bUsePawnControlRotation=!bObserve;
 if(bObserve && Phase!=EFishingPhase::Landed){for(TActorIterator<AExponentialHeightFog> I(GetWorld());I;++I){I->GetComponent()->SetFogDensity(.16f);I->GetComponent()->SetFogHeightFalloff(.001f);I->GetComponent()->SetFogInscatteringColor(FLinearColor(.015f,.095f,.075f));}}
 else {ApplyEnvironment();for(TActorIterator<AExponentialHeightFog> I(GetWorld());I;++I)I->GetComponent()->SetFogHeightFalloff(.16f);}Rig->SetVisibility(!bObserve,true);
 if(!bObserve){Camera->SetRelativeLocation(FVector(0,0,170));Camera->SetRelativeRotation(FRotator::ZeroRotator);}
}
void ALurePawn::UpdateRig(float Dt){
 Rig->SetVisibility(!bObserve && Phase!=EFishingPhase::Landed && Phase!=EFishingPhase::Releasing,true);
 CrankAngle+=Reeling?Dt*600:0;
 float Kick=Phase==EFishingPhase::Flying?FMath::Exp(-PhaseTime*7)*18:0;
 if(bUseAuthoredRig){
  Rig->SetRelativeLocation(FVector(0,0,FMath::Sin(Clock*1.8f)*.25f));
  Rig->SetRelativeRotation(FRotator(Charge*48-Kick-RodLoad()*8+RodLiftInput*8+Impact*2,RodSideInput*7,-RodSideInput*5));
  for(auto* Old:{Rod,RightArm,LeftArm,Crank})Old->SetVisibility(false);
  AuthoredRig->SetVisibility(!bObserve && Phase!=EFishingPhase::Landed && Phase!=EFishingPhase::Releasing);
  AuthoredRig->SetPosition(FMath::Fmod(CrankAngle/360.f*2.f,2.f),false);
  AuthoredRig->TickAnimation(0.f,false);AuthoredRig->RefreshBoneTransforms();
  const FVector Origin=AuthoredRig->GetSocketLocation(TEXT("FP_Rod"));
  const FVector Axis=(AuthoredRig->GetSocketLocation(TEXT("FP_Tip"))-Origin)/210.f;
  const FVector Bend=RodBend();
  for(int i=0;i<Blank.Num();++i){
   float A=float(i)/Blank.Num(),B=float(i+1)/Blank.Num();
   FVector P=Origin+Axis*(18+A*192)+Bend*A*A,Q=Origin+Axis*(18+B*192)+Bend*B*B,D=Q-P;
   Blank[i]->SetWorldLocation((P+Q)*.5f);Blank[i]->SetWorldRotation(FRotationMatrix::MakeFromZ(D).Rotator());
   float Radius=FMath::Lerp(.007f,.0013f,A);Blank[i]->SetWorldScale3D(FVector(Radius,Radius,D.Size()/100+.001f));
  }
  for(int i=0;i<Guides.Num();++i){
   float A=float(i+1)/Guides.Num();Guides[i]->SetWorldLocation(Origin+Axis*(18+A*192)+Bend*A*A-Camera->GetUpVector()*1.2f);
   Guides[i]->SetWorldRotation(FRotationMatrix::MakeFromX(Axis).Rotator());Guides[i]->SetWorldScale3D(FVector(1-A*.7f));
  }
  return;
 }
 Rig->SetRelativeRotation(FRotator(8+Charge*48-Kick-Tension*8,-12,0));
 Rig->SetRelativeLocation(FVector(65,22,-20+FMath::Sin(Clock*1.8f)*.25f));
 // A spinning-reel crank turns about the transverse spindle, not the rod axis.
 Crank->SetRelativeRotation(FRotator(CrankAngle,0,0));
 // Follow the exported knob through the actual crank transform, including
 // Unreal's roll convention, instead of maintaining a second rotation formula.
 const FVector KnobLocal(4.485f,-7.0f,-3.1f);
 const FVector HandContactOffset(4.8f,2.8f,0);
 LeftArm->SetRelativeLocation(Crank->GetRelativeTransform().TransformPosition(KnobLocal)+HandContactOffset);
 for(int i=0;i<Blank.Num();++i){
  float A=float(i)/Blank.Num(),B=float(i+1)/Blank.Num();
  FVector P(18+A*192,0,-Tension*42*A*A),Q(18+B*192,0,-Tension*42*B*B),D=Q-P;
  Blank[i]->SetRelativeLocation((P+Q)*.5f);Blank[i]->SetRelativeRotation(FRotationMatrix::MakeFromZ(D).Rotator());
  float Radius=FMath::Lerp(.007f,.0013f,A);Blank[i]->SetRelativeScale3D(FVector(Radius,Radius,D.Size()/100+.001f));
 }
 for(int i=0;i<Guides.Num();++i){float A=float(i+1)/Guides.Num();Guides[i]->SetRelativeLocation(FVector(18+A*192,0,-Tension*42*A*A-1.2f));Guides[i]->SetRelativeScale3D(FVector(1-A*.7f));}
}
void ALurePawn::InitializeAuthoredRig(){
 auto* Mesh=LoadObject<USkeletalMesh>(nullptr,TEXT("/Game/FirstPerson/AuthoredLegacy/SK_AuthoredFishingRig.SK_AuthoredFishingRig"));
 auto* Animation=LoadObject<UAnimSequence>(nullptr,TEXT("/Game/FirstPerson/AuthoredLegacy/A_AuthoredReel.A_AuthoredReel"));
 if(!Mesh || !Animation){UE_LOG(LogTemp,Error,TEXT("AUTHORED_RIG: mesh or animation missing"));return;}
 AuthoredRig->SetSkeletalMeshAsset(Mesh);AuthoredRig->SetAnimationMode(EAnimationMode::AnimationSingleNode);
 AuthoredRig->SetAnimation(Animation);AuthoredRig->SetPosition(0,false);
 AuthoredRig->TickAnimation(0,false);AuthoredRig->RefreshBoneTransforms();
 auto Point=[&](const TCHAR* Name){return AuthoredRig->GetSocketTransform(Name,RTS_Component).GetLocation();};
 FVector Eye=Point(TEXT("FP_View")),Forward=Point(TEXT("FP_Aim"))-Eye,Up=Point(TEXT("FP_Up"))-Eye;
 if(Forward.Size()<10 || Up.Size()<10){UE_LOG(LogTemp,Error,TEXT("AUTHORED_RIG: invalid camera markers"));return;}
 const FTransform View(FRotationMatrix::MakeFromXZ(Forward,Up).ToQuat(),Eye);
 if(FParse::Param(FCommandLine::Get(),TEXT("LureRigReview"))){
  const FVector Right0=Point(TEXT("hand_r")),Left0=Point(TEXT("hand_l")),Rod0=Point(TEXT("FP_Rod"));
  AuthoredRig->SetPosition(1.f,false);AuthoredRig->TickAnimation(0,false);AuthoredRig->RefreshBoneTransforms();
  float LeftTravel=(Point(TEXT("hand_l"))-Left0).Size(),RightDrift=(Point(TEXT("hand_r"))-Right0).Size(),RodDrift=(Point(TEXT("FP_Rod"))-Rod0).Size();
  UE_LOG(LogTemp,Display,TEXT("AUTHORED_ANIMATION %s left_travel_cm=%.3f right_drift_cm=%.5f rod_drift_cm=%.5f"),LeftTravel>1.f && RightDrift<.1f && RodDrift<.1f?TEXT("PASS"):TEXT("FAIL"),LeftTravel,RightDrift,RodDrift);
  AuthoredRig->SetPosition(0,false);AuthoredRig->TickAnimation(0,false);AuthoredRig->RefreshBoneTransforms();
 }
 FTransform Placement=View.Inverse();Placement.AddToTranslation(FVector(12,12,-9));
 AuthoredRig->SetRelativeTransform(Placement);bUseAuthoredRig=true;
 UE_LOG(LogTemp,Display,TEXT("AUTHORED_RIG: active bones=%d view=%s forward_length=%.3f rod_length=%.3f"),AuthoredRig->GetNumBones(),*Eye.ToString(),Forward.Size(),(Point(TEXT("FP_Tip"))-Point(TEXT("FP_Rod"))).Size());
}
FVector ALurePawn::RodTip() const{
 return bUseAuthoredRig?AuthoredRig->GetSocketLocation(TEXT("FP_Tip"))+RodBend():
  Rig->GetComponentTransform().TransformPosition(FVector(210,0,-Tension*42));
}
void ALurePawn::UpdateFish(float Dt){
 const float Speeds[]={180.f,120.f,220.f,110.f,100.f};
 FLurePresentation Presentation;Presentation.RetrieveSpeed=Reeling?Speeds[LureType]:0;
 Presentation.PauseSeconds=Reeling?0:Clock-LastReelStop;Presentation.TwitchAge=Clock-LastTwitch;Presentation.LureType=LureType;
 ALureFish* Responding=nullptr;float BestResponse=MAX_flt;
 if(Phase==EFishingPhase::Retrieving)for(auto* F:Fish){
  if(!IsValid(F) || F->HabitatIndex<0 || !F->CanRespondToLure(LurePosition))continue;
  const bool Following=F->Behavior==EFishBehavior::Following || F->Behavior==EFishBehavior::Hesitating || F->Behavior==EFishBehavior::Attacking;
  const float Score=FVector::DistSquared(F->GetActorLocation(),LurePosition)*(Following?.08f:1.f);
  if(Score<BestResponse){BestResponse=Score;Responding=F;}
 }
 for(auto* F:Fish){
  if(!IsValid(F))continue;
  if(F==ActiveFish && (Phase==EFishingPhase::Fighting || Phase==EFishingPhase::Bite || Phase==EFishingPhase::Landing)){F->SetHooked(LurePosition,Clock);continue;}
  if(F==ActiveFish && (Phase==EFishingPhase::Landed || Phase==EFishingPhase::Releasing))continue;
  F->Activity=(Weather==3?1.2f:1.f)*(TimeOfDay==0||TimeOfDay==2?1.15f:.8f)*(LureType==F->Species%5?1.3f:1.f);
  bool Attack=F->Simulate(Dt,LurePosition,Phase==EFishingPhase::Retrieving && (F->HabitatIndex<0 || F==Responding),Presentation);
  if(Attack && Phase==EFishingPhase::Retrieving){ActiveFish=F;BiteWindow=F->StrikeWindow;SetPhase(EFishingPhase::Bite);ReelStop();SplashPosition=LurePosition;SplashPosition.Z=0;SplashTime=Clock;PlayCue(TEXT("Bite"));Impact=.7f;Notice=TEXT("咬口！按空格刺鱼！");UE_LOG(LogTemp,Display,TEXT("ENCOUNTER_BITE species=%d window=%.2f natural=true"),F->Species,BiteWindow);}
  else if(Phase==EFishingPhase::Retrieving && F->InterestLevel>.4f && Clock-LastFollowCue>5.f && FVector::Dist2D(F->GetActorLocation(),LurePosition)<550){
   LastFollowCue=Clock;
   if(F->GetActorLocation().Z>-125.f){SplashPosition=F->GetActorLocation();SplashPosition.Z=0;SplashTime=Clock;SurfaceCue(F->GetActorLocation(),.65f);}
   if(HasFishingAssist())Announce(F->Behavior==EFishBehavior::Hesitating?TEXT("它在犹豫…"):TEXT("水下有动静"),TEXT("试试停顿，给它一个攻击机会"),1.8f,.07f);
  }
 }
}
FString ALurePawn::FishStatus() const {
 for(auto* F:Fish)if(F->Behavior==EFishBehavior::Attacking)return TEXT("它加速了，留意下一下顿口！");
 for(auto* F:Fish)if(F->Behavior==EFishBehavior::Hesitating)return TEXT("鱼在犹豫，改变收线节奏");
 for(auto* F:Fish)if(F->Behavior==EFishBehavior::Following)return TEXT("有鱼正在追饵，试试停顿或轻抽");
 return TEXT("留意沉木与石边，改变收线节奏");
}

ALureGameMode::ALureGameMode(){DefaultPawnClass=ALurePawn::StaticClass(); HUDClass=ALureHUD::StaticClass();}
void ALureGameMode::BeginPlay(){
 Super::BeginPlay();
 for(TActorIterator<ACoveEnvironment> It(GetWorld());It;++It)return;

 auto* Shore=Place(GetWorld(),TEXT("Cube"),FVector::ZeroVector,FVector::OneVector,FLinearColor(.12f,.14f,.06f));
 Shore->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Bank.SM_Bank")));
 Shore->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
 auto* FarShore=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(7000,0,0),FRotator(0,180,0));
 FarShore->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
 FarShore->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Bank.SM_Bank")));
 FarShore->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
 auto* Bed=Place(GetWorld(),TEXT("Cube"),FVector(3500,0,-440),FVector(70,100,1),FLinearColor(.14f,.17f,.095f));
 Bed->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
 auto* Water=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(0,5000,0),FRotator::ZeroRotator);
 Water->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
 Water->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_WaterGrid.SM_WaterGrid")));
 Water->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_LakeWater.M_LakeWater")));
 Water->SetActorScale3D(FVector(70,100,1));Water->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Water->GetStaticMeshComponent()->SetCastShadow(false);
 auto Instances=[&](const TCHAR* Name,UStaticMesh* M,FLinearColor C){
  auto* A=GetWorld()->SpawnActor<AActor>();auto* I=NewObject<UInstancedStaticMeshComponent>(A,Name);A->SetRootComponent(I);I->SetStaticMesh(M);I->SetCollisionEnabled(ECollisionEnabled::NoCollision);I->RegisterComponent();Tint(I,C);return I;
 };
 auto* Rocks=Instances(TEXT("Rocks"),LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Rock.SM_Rock")),FLinearColor(.13f,.145f,.12f));
 auto* Trees=Instances(TEXT("Forest"),LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Birch.SM_Birch")),FLinearColor(.04f,.08f,.03f));
 Trees->EmptyOverrideMaterials(); Rocks->EmptyOverrideMaterials();
 FRandomStream Rng(712);
 for(int i=0;i<100;++i){float Y=Rng.FRandRange(-5000,5000);FVector Pos(Rng.FRandRange(-70,120),Y,Rng.FRandRange(-50,0));Rocks->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),Pos,FVector(Rng.FRandRange(.5f,1.6f),Rng.FRandRange(.7f,2),Rng.FRandRange(.5f,1))),true);}
 for(int i=0;i<12;++i)Rocks->AddInstance(FTransform(FRotator(0,i*63,0),FVector(1650+i*65,850+FMath::Sin(i*2.f)*130,-50),FVector(1.2f,1.1f,1)),true);
 auto* Log=Place(GetWorld(),TEXT("Cylinder"),FVector(2150,700,0),FVector(.25f,.25f,5),FLinearColor(.09f,.045f,.019f));Log->SetActorRotation(FRotator(83,30,0));
 for(int i=0;i<240;++i){
  const bool Far=i>60;const float X=Far?Rng.FRandRange(7250,10100):Rng.FRandRange(-2600,-1450),Y=Rng.FRandRange(-5200,5200),H=Rng.FRandRange(650,1600);
  Trees->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),FVector(X,Y,Far?50:65),FVector(H/850)),true);

 }
 for(int i=0;i<30;++i)Rocks->AddInstance(FTransform(FRotator(0,i*39,0),FVector(7000,Rng.FRandRange(-6500,6500),-70),FVector(Rng.FRandRange(3,8),Rng.FRandRange(4,8),Rng.FRandRange(3,6))),true);
 // Textured grass clumps have individual blades and cutout leaf edges.
 auto* Grass=Instances(TEXT("BankGrass"),LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Grass.SM_Grass")),FLinearColor::White);
 Grass->EmptyOverrideMaterials();
 for(int i=0;i<1500;++i){float X=Rng.FRandRange(-1450,-80),Y=Rng.FRandRange(-4500,4500);if(X>-650 && FMath::Abs(Y)<240)continue;float S=Rng.FRandRange(.6f,1.6f);Grass->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),FVector(X,Y,45),FVector(S)),true);}
 auto* Sun=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,2000),FRotator(-24,-28,0));Sun->GetLightComponent()->SetMobility(EComponentMobility::Movable);Sun->GetLightComponent()->SetIntensity(3.f);Sun->GetLightComponent()->SetLightColor(FLinearColor(1,.88f,.7f));
 Cast<UDirectionalLightComponent>(Sun->GetLightComponent())->SetAtmosphereSunLight(true);
 GetWorld()->SpawnActor<ASkyAtmosphere>();
 auto* Dome=GetWorld()->SpawnActor<AStaticMeshActor>();Dome->Tags.Add(TEXT("SkyDome"));Dome->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);Dome->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/EngineSky/SM_SkySphere.SM_SkySphere")));Dome->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Dome->GetStaticMeshComponent()->SetCastShadow(false);Dome->SetActorScale3D(FVector(400));
 auto* SkyMat=UMaterialInstanceDynamic::Create(LoadObject<UMaterialInterface>(nullptr,TEXT("/Engine/EngineSky/M_Sky_Panning_Clouds2.M_Sky_Panning_Clouds2")),Dome);Dome->GetStaticMeshComponent()->SetMaterial(0,SkyMat);

 auto* Sky=GetWorld()->SpawnActor<ASkyLight>();Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);Sky->GetLightComponent()->SetIntensity(.8f);Sky->GetLightComponent()->RecaptureSky();
 auto* Fog=GetWorld()->SpawnActor<AExponentialHeightFog>();Fog->GetComponent()->SetFogDensity(.008f);Fog->GetComponent()->SetFogHeightFalloff(.16f);Fog->GetComponent()->SetFogInscatteringColor(FLinearColor(.3f,.4f,.42f));
 auto* Post=GetWorld()->SpawnActor<APostProcessVolume>();Post->bUnbound=true;Post->Settings.bOverride_AutoExposureBias=true;Post->Settings.AutoExposureBias=-.5f;
 Post->Settings.bOverride_MotionBlurAmount=true;Post->Settings.MotionBlurAmount=0;
 if(auto* P=Cast<ALurePawn>(UGameplayStatics::GetPlayerPawn(this,0)))P->ApplyEnvironment();

}
void ALurePawn::RunSmokeTest() {
 int Failures=0;
 auto Check=[&](bool Pass,const TCHAR* Label){ UE_LOG(LogTemp,Display,TEXT("LURE_TEST %s: %s"),Pass?TEXT("PASS"):TEXT("FAIL"),Label); if(!Pass) ++Failures; };
 auto Step=[&](int Frames){for(int i=0;i<Frames;++i) Tick(1.f/60.f);};
 // The bite scenario targets the stocked centre of the lake. Do not inherit
 // the presentation camera's initial yaw, which may aim outside fish habitat.
 if(auto* PC=Cast<APlayerController>(GetController()))PC->SetControlRotation(FRotator(-7,0,0));
 Camera->SetWorldRotation(FRotator(-7,0,0));
 Check(Phase==EFishingPhase::Ready,TEXT("initial ready state"));
 PressCast(); Step(90); Check(Charge>0.99f,TEXT("full charge"));
 ReleaseCast(); Check(Phase==EFishingPhase::Flying,TEXT("cast launches"));
 for(int i=0;i<600 && Phase==EFishingPhase::Flying;++i) Tick(1.f/60.f);
 Check(Phase==EFishingPhase::Retrieving && DistanceMetres()>10,TEXT("cast enters lake"));
 float NearestFish=MAX_flt;for(auto* F:Fish)NearestFish=FMath::Min(NearestFish,FVector::Distance(F->GetActorLocation(),LurePosition));
 UE_LOG(LogTemp,Display,TEXT("LURE_TEST_SCENARIO lure=%s nearest_fish_cm=%.1f"),*LurePosition.ToString(),NearestFish);
 auto Present=[&](){for(int i=0;i<6000 && Phase==EFishingPhase::Retrieving;++i){
  const float Cycle=FMath::Fmod(i/60.f,2.8f);if(Cycle<1.4f)ReelStart();else ReelStop();
  if(i%168==60)Strike();Tick(1.f/60.f);
 }};
 Present();
 Check(Phase==EFishingPhase::Bite,TEXT("retrieve cadence produces a natural bite"));
 Step(90); Check(Phase==EFishingPhase::Retrieving,TEXT("missed bite returns to retrieve"));
 Present();Step(FMath::RoundToInt(BiteWindow*.43f*60));
 Strike(); Check(Phase==EFishingPhase::Fighting,TEXT("strike hooks fish"));
 for(int i=0;i<12000 && Phase==EFishingPhase::Fighting;++i){
  Drag=Fight.IsSurging()?.28f:.57f;if(Fight.Move==EFightMove::Recover||Fight.Energy<.1f)ReelStart();else ReelStop();
  const float Lift=Fight.Move==EFightMove::Dive?1.f:(Fight.Move==EFightMove::Jump?-1.f:0.f);
  if(auto* PC=Cast<APlayerController>(GetController()))PC->SetControlRotation(FRotator(HookFacingPitch+Lift*25,HookFacingYaw+Fight.RequiredSide()*30,0));
  Tick(1.f/60.f);
 }
 Check(Phase==EFishingPhase::Landing && Catches==0,TEXT("controlled fight reaches netting window without automatic catch"));
 Strike();Check(Phase==EFishingPhase::Landed && Catches==1 && CatchScore>0,TEXT("netting completes catch and rewards"));
 ResetCast(); SwitchLure(); Check(LureType==1 && Phase==EFishingPhase::Ready,TEXT("reset and change lure"));
 LurePosition=FVector(2000,0,0); ActiveFish=Fish[0]; SetPhase(EFishingPhase::Bite); Strike(); Drag=1; ReelStart();
 for(int i=0;i<1800 && Phase==EFishingPhase::Fighting;++i) Tick(1.f/60.f);
 Check(Phase==EFishingPhase::Ready && Notice.Contains(TEXT("断线")),TEXT("excessive drag breaks line"));
 UE_LOG(LogTemp,Display,TEXT("LURE_TEST COMPLETE failures=%d"),Failures);
 FPlatformMisc::RequestExitWithStatus(false,Failures?1:0);
}




void ALurePawn::RunInputTest(){
 auto* PC=Cast<APlayerController>(GetController());int Failures=0;
 auto Check=[&](bool Pass,const TCHAR* Name){UE_LOG(LogTemp,Display,TEXT("LURE_INPUT %s: %s"),Pass?TEXT("PASS"):TEXT("FAIL"),Name);if(!Pass)++Failures;};
 Check(PC && PC->PlayerInput && InputComponent,TEXT("player input and bindings initialized"));
 if(PC && PC->PlayerInput && InputComponent){
  const FVector Before=GetActorLocation();const FRotator BeforeRot=PC->GetControlRotation(); FrameDelta=1.f/60.f;
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Pressed,1));
  for(int i=0;i<60;++i){
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseX,IE_Axis,4,1));
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseY,IE_Axis,1,1));
   PC->PlayerInput->Tick(1.f/60.f);PC->PlayerInput->ProcessInputStack({InputComponent},1.f/60.f,false);
   PC->UpdateRotation(1.f/60.f);PC->RotationInput=FRotator::ZeroRotator;MoveForward(PC->IsInputKeyDown(EKeys::W)?1:0);
  }
  Check(FVector::Dist(Before,GetActorLocation())>5,TEXT("held W moves player"));
  Check(FMath::Abs(FMath::FindDeltaAngleDegrees(BeforeRot.Yaw,PC->GetControlRotation().Yaw))>10,TEXT("mouse yaw changes while W held"));
  Check(FMath::Abs(FMath::FindDeltaAngleDegrees(BeforeRot.Pitch,PC->GetControlRotation().Pitch))>2,TEXT("mouse pitch changes while W held"));
  FMinimalViewInfo View;Camera->GetCameraView(0,View);
  Check(FMath::Abs(FMath::FindDeltaAngleDegrees(View.Rotation.Yaw,PC->GetControlRotation().Yaw))<1,TEXT("camera follows controller rotation"));
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::W,IE_Released,0));PC->PlayerInput->ProcessInputStack({InputComponent},1.f/60.f,false);
  Check(!PC->IsInputKeyDown(EKeys::W),TEXT("released movement key clears"));
  if(auto* VP=GetWorld()->GetGameViewport())Check(VP->GetMouseCaptureMode()==EMouseCaptureMode::CapturePermanently_IncludingInitialMouseDown,TEXT("persistent mouse capture configured"));
  UE_LOG(LogTemp,Display,TEXT("LURE_INPUT movement=%.2f yaw=%.2f pitch=%.2f"),FVector::Dist(Before,GetActorLocation()),PC->GetControlRotation().Yaw-BeforeRot.Yaw,PC->GetControlRotation().Pitch-BeforeRot.Pitch);

  // Exercise the observation transition with each movement key independently,
  // so opposite directions cannot cancel and hide an unintended movement.
  SetPhase(EFishingPhase::Landed);
  SetActorLocation(FVector(-550,0,Cove::Height(-550,0)));
  PC->SetControlRotation(FRotator::ZeroRotator);
  auto ToggleObservation=[&](){
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::V,IE_Pressed,1));
   PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::V,IE_Released,0));
   PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);
  };
  auto StepMovementAndLook=[&](){
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseX,IE_Axis,1,1));
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::MouseY,IE_Axis,.5f,1));
   PC->PlayerInput->Tick(FrameDelta);PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);
   PC->UpdateRotation(FrameDelta);PC->RotationInput=FRotator::ZeroRotator;
   MoveForward(float(PC->IsInputKeyDown(EKeys::W))-float(PC->IsInputKeyDown(EKeys::S)));
   MoveRight(float(PC->IsInputKeyDown(EKeys::D))-float(PC->IsInputKeyDown(EKeys::A)));
  };
  ToggleObservation();
  Check(bObserve && !Camera->bUsePawnControlRotation,TEXT("V enters observation mode"));
  const FRotator ObservedRotation=PC->GetControlRotation();
  const FKey MovementKeys[]={EKeys::W,EKeys::S,EKeys::A,EKeys::D};
  for(const FKey& Key:MovementKeys){
   const FVector Position=GetActorLocation();
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Pressed,1));
   for(int i=0;i<10;++i)StepMovementAndLook();
   Check(GetActorLocation().Equals(Position,.001f),*FString::Printf(TEXT("observation blocks held %s"),*Key.ToString()));
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Released,0));
   PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);
  }
  Check(PC->GetControlRotation().Equals(ObservedRotation,.001f),TEXT("observation blocks mouse look"));
  ToggleObservation();
  Check(!bObserve && Camera->bUsePawnControlRotation,TEXT("V exits observation and restores camera control"));
  const FRotator ResumedRotation=PC->GetControlRotation();
  for(const FKey& Key:MovementKeys){
   const FVector Position=GetActorLocation();
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Pressed,1));
   for(int i=0;i<10;++i)StepMovementAndLook();
   Check(FVector::Dist2D(Position,GetActorLocation())>5,*FString::Printf(TEXT("exiting observation restores held %s movement"),*Key.ToString()));
   PC->InputKey(FInputKeyEventArgs::CreateSimulated(Key,IE_Released,0));
   PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);
  }
  Check(FMath::Abs(FMath::FindDeltaAngleDegrees(ResumedRotation.Yaw,PC->GetControlRotation().Yaw))>1,TEXT("exiting observation restores mouse yaw while moving"));
  Check(FMath::Abs(FMath::FindDeltaAngleDegrees(ResumedRotation.Pitch,PC->GetControlRotation().Pitch))>1,TEXT("exiting observation restores mouse pitch while moving"));
  Camera->GetCameraView(0,View);
  Check(View.Rotation.Equals(PC->GetControlRotation(),.01f),TEXT("camera follows controller after observation"));
  // Keyboard counter-steering must remain authoritative after a large mouse turn.
  SetPhase(EFishingPhase::Fighting);Fight.Start(1.5f,0,.9f,24);
  HookFacingYaw=HookFacingPitch=0;PC->SetControlRotation(FRotator(50,60,0));
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::A,IE_Pressed,1));
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::S,IE_Pressed,1));
  PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);TickEncounter(FrameDelta);
  Check(RodSideInput== -1.f && RodLiftInput== -1.f,TEXT("keyboard counter-steering overrides opposite mouse offset"));
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::A,IE_Released,0));
  PC->InputKey(FInputKeyEventArgs::CreateSimulated(EKeys::S,IE_Released,0));
  PC->PlayerInput->ProcessInputStack({InputComponent},FrameDelta,false);
  Fight.Distance=5.9f;Fight.LateralOffset=9;Fight.Energy=.1f;Fight.Move=EFightMove::Jump;Fight.MoveTime=1.1f;Fight.MoveDuration=2;
  TickEncounter(FrameDelta);
  Check(FMath::IsNearlyEqual(DistanceMetres(),Fight.Distance,.01f),TEXT("fight display distance includes lateral movement"));
  Check(Phase==EFishingPhase::Landing && LurePosition.Z<0 && Fight.JumpHeight==0,TEXT("landing brings jumping fish back to water"));
  PhaseTime=4.1f;TickEncounter(FrameDelta);
  Check(Phase==EFishingPhase::Fighting && Fight.Distance==7.f,TEXT("missed netting window gives fish another run"));
  ResetCast();
 }
 UE_LOG(LogTemp,Display,TEXT("LURE_INPUT COMPLETE failures=%d"),Failures);FPlatformMisc::RequestExitWithStatus(false,Failures?1:0);
}





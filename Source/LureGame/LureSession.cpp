#include "LureWorld.h"
#include "CoveTerrain.h"
#include "LureSave.h"
#include "FishingVisuals.h"
#include "Kismet/GameplayStatics.h"
#include "Components/AudioComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyLightComponent.h"
#include "Components/ExponentialHeightFogComponent.h"
#include "Camera/CameraComponent.h"
#include "Engine/DirectionalLight.h"
#include "Engine/StaticMeshActor.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/SkyLight.h"
#include "Engine/ExponentialHeightFog.h"
#include "GameFramework/GameUserSettings.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"
#include "Sound/SoundBase.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"
#include "HAL/PlatformMisc.h"
namespace { bool IsTesting(){return FParse::Param(FCommandLine::Get(),TEXT("LureSmokeTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureInputTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureSessionTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))||FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"));} }
FString ALurePawn::LureName() const {const TCHAR* N[]={TEXT("悬浮米诺"),TEXT("软虫"),TEXT("旋转亮片"),TEXT("水面波爬"),TEXT("铅头钩")};return N[LureType%5];}
FString ALurePawn::WeatherName() const {const TCHAR* N[]={TEXT("晴朗"),TEXT("阴天"),TEXT("薄雾"),TEXT("小雨")};return N[Weather%4];}
FString ALurePawn::TimeName() const {const TCHAR* N[]={TEXT("清晨 06:30"),TEXT("午后 14:00"),TEXT("黄昏 18:20"),TEXT("夜晚 21:00")};return N[TimeOfDay%4];}
FString ALurePawn::SpotName() const {const TCHAR* N[]={TEXT("沉木湾"),TEXT("芦苇浅滩"),TEXT("岩石岬角")};return N[Spot%3];}
void ALurePawn::SessionInit(){
 if(!IsTesting())SaveData=Cast<ULureSave>(UGameplayStatics::LoadGameFromSlot(TEXT("WildwaterV1"),0));
 if(!SaveData)SaveData=NewObject<ULureSave>(this);
 Sensitivity=FMath::Clamp(SaveData->Sensitivity,.04f,.4f);Volume=FMath::Clamp(SaveData->Volume,0.f,1.f);Weather=FMath::Clamp(SaveData->Weather,0,3);TimeOfDay=FMath::Clamp(SaveData->TimeOfDay,0,3);Spot=FMath::Clamp(SaveData->Spot,0,2);Catches=SaveData->TotalCatches;{const float Y=Spot==0?0:(Spot==1?-1600:1600);SetActorLocation(FVector(-420,Y,Cove::Height(-420,Y)));}
 if(auto* Audio=LoadObject<USoundBase>(nullptr,TEXT("/Game/Audio/Ambient.Ambient")))AmbientAudio=UGameplayStatics::SpawnSound2D(this,Audio,Volume*.55f,1,0,nullptr,true,false);
 if(auto* Audio=LoadObject<USoundBase>(nullptr,TEXT("/Game/Audio/Reel.Reel"))){ReelAudio=UGameplayStatics::SpawnSound2D(this,Audio,0,1,0,nullptr,true,false);}
 Rain=NewObject<UInstancedStaticMeshComponent>(this,TEXT("Rain"));Rain->SetupAttachment(RootComponent);Rain->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));Rain->SetCollisionEnabled(ECollisionEnabled::NoCollision);Rain->SetCastShadow(false);Rain->RegisterComponent();
 for(int i=0;i<130;++i)Rain->AddInstance(FTransform(FRotator::ZeroRotator,FVector::ZeroVector,FVector(.003f,.003f,.25f)));
 if(!IsTesting() || FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"))){
  bMenuOpen=true;MenuPage=0;Rig->SetVisibility(false,true);
  if(auto* PC=Cast<APlayerController>(GetController())){PC->SetInputMode(FInputModeGameAndUI());PC->bShowMouseCursor=true;}
  auto* Settings=UGameUserSettings::GetGameUserSettings();Settings->SetOverallScalabilityLevel(FMath::Clamp(SaveData->Quality,0,2));Settings->SetFrameRateLimit(60);Settings->ApplyNonResolutionSettings();
 }
 auto* Graphics=UGameUserSettings::GetGameUserSettings();Graphics->SetOverallScalabilityLevel(FMath::Clamp(SaveData->Quality,0,2));Graphics->SetFrameRateLimit(60);Graphics->ApplyNonResolutionSettings();
 ApplyEnvironment();
}
void ALurePawn::SaveSession(){
 if(!SaveData || IsTesting())return;
 SaveData->Sensitivity=Sensitivity;SaveData->Volume=Volume;SaveData->Weather=Weather;SaveData->TimeOfDay=TimeOfDay;SaveData->Spot=Spot;SaveData->TotalCatches=Catches;
 if(!UGameplayStatics::SaveGameToSlot(SaveData,TEXT("WildwaterV1"),0))Notice=TEXT("存档写入失败，请检查磁盘空间。");
}
void ALurePawn::PlayCue(const TCHAR* Name){FString P=FString::Printf(TEXT("/Game/Audio/%s.%s"),Name,Name);if(auto* S=LoadObject<USoundBase>(nullptr,*P))UGameplayStatics::PlaySound2D(this,S,Volume*.7f);}
void ALurePawn::RecordCatch(){
 if(!ActiveFish || !SaveData)return;
 FCatchRecord R;R.Species=ActiveFish->SpeciesName();R.Weight=ActiveFish->Weight;R.Length=ActiveFish->Body->Bounds.BoxExtent.X*2+10*ActiveFish->SizeFactor;R.Date=FDateTime::Now().ToString(TEXT("%Y-%m-%d %H:%M"));R.Lure=LureName();
 SaveData->BestWeight=FMath::Max(SaveData->BestWeight,R.Weight);
 SaveData->Journal.Insert(R,0);if(SaveData->Journal.Num()>100)SaveData->Journal.SetNum(100);
 LastCatch=FString::Printf(TEXT("%s  ·  %.2f kg  ·  %.0f cm"),*R.Species,R.Weight,R.Length);SaveSession();PlayCue(TEXT("Catch"));
}
void ALurePawn::MenuAction(const FString& A){
 if(A==TEXT("play")){
  bMenuOpen=false;bStarted=true;Rig->SetVisibility(!bObserve,true);CaptureMouse();Notice=TEXT("向湖面瞄准，按住左键蓄力，松开抛投。Tab 切换拟饵。");SaveSession();
 }else if(A==TEXT("settings"))MenuPage=1;
 else if(A==TEXT("journal"))MenuPage=2;
 else if(A==TEXT("help"))MenuPage=3;
 else if(A==TEXT("back"))MenuPage=0;
 else if(A==TEXT("quit")){SaveSession();FPlatformMisc::RequestExit(false);}
 else if(A==TEXT("weather")){Weather=(Weather+1)%4;ApplyEnvironment();}
 else if(A==TEXT("time")){TimeOfDay=(TimeOfDay+1)%4;ApplyEnvironment();}
 else if(A==TEXT("spot")){
  ResetCast();Spot=(Spot+1)%3;{const float Y=Spot==0?0:(Spot==1?-1600:1600);SetActorLocation(FVector(-420,Y,Cove::Height(-420,Y)));}
  if(auto* PC=Cast<APlayerController>(GetController()))PC->SetControlRotation(FRotator(-8,Spot==1?-20:(Spot==2?-55:-40),0));
  Notice=TEXT("已收竿并移动到新标点。");
 }else if(A==TEXT("sens+"))Sensitivity=FMath::Min(.4f,Sensitivity+.02f);
 else if(A==TEXT("sens-"))Sensitivity=FMath::Max(.04f,Sensitivity-.02f);
 else if(A==TEXT("volume+"))Volume=FMath::Min(1.f,Volume+.1f);
 else if(A==TEXT("volume-"))Volume=FMath::Max(0.f,Volume-.1f);
 else if(A==TEXT("quality")){SaveData->Quality=(SaveData->Quality+1)%3;auto* Q=UGameUserSettings::GetGameUserSettings();Q->SetOverallScalabilityLevel(SaveData->Quality);Q->ApplyNonResolutionSettings();}
 else if(A==TEXT("fullscreen")){SaveData->bFullscreen=!SaveData->bFullscreen;auto* Q=UGameUserSettings::GetGameUserSettings();Q->SetFullscreenMode(SaveData->bFullscreen?EWindowMode::WindowedFullscreen:EWindowMode::Windowed);Q->ApplyResolutionSettings(false);}
 SaveSession();
}
void ALurePawn::ApplyEnvironment(){
 const float Pitch[]={-15.f,-58.f,-8.f,-25.f};const float Lux[]={30000.f,55000.f,12000.f,.12f};
 const FLinearColor Colors[]={FLinearColor(1,.8f,.58f),FLinearColor(1,.96f,.89f),FLinearColor(1,.5f,.23f),FLinearColor(.38f,.52f,1)};
 for(TActorIterator<ADirectionalLight> I(GetWorld());I;++I){I->SetActorRotation(FRotator(Pitch[TimeOfDay],TimeOfDay==2?30:-95,0));I->GetLightComponent()->SetIntensity(Lux[TimeOfDay]*(Weather==0?1.f:.4f));I->GetLightComponent()->SetLightColor(Colors[TimeOfDay]);}
 for(TActorIterator<AStaticMeshActor> I(GetWorld());I;++I)if(I->Tags.Contains(TEXT("SkyDome"))){
  if(auto* M=Cast<UMaterialInstanceDynamic>(I->GetStaticMeshComponent()->GetMaterial(0))){
   bool Night=TimeOfDay==3;M->SetScalarParameterValue(TEXT("Cloud speed"),Weather==3?1.f:.2f);M->SetScalarParameterValue(TEXT("Cloud opacity"),Weather==0?.35f:1.5f);M->SetScalarParameterValue(TEXT("Stars brightness"),Night?1.f:0.f);M->SetScalarParameterValue(TEXT("Sun brightness"),Night?.1f:15.f);M->SetScalarParameterValue(TEXT("Sun height"),.3f);M->SetScalarParameterValue(TEXT("Sun Radius"),.015f);
   M->SetVectorParameterValue(TEXT("Overall Color"),FLinearColor::White);
   M->SetVectorParameterValue(TEXT("Zenith Color"),Night?FLinearColor(.001f,.003f,.015f):FLinearColor(.045f,.14f,.27f));
   M->SetVectorParameterValue(TEXT("Horizon color"),Night?FLinearColor(.012f,.02f,.04f):(TimeOfDay==2?FLinearColor(.55f,.23f,.11f):FLinearColor(.48f,.6f,.62f)));
   M->SetVectorParameterValue(TEXT("Cloud color"),Night?FLinearColor(.015f,.024f,.04f):(Weather==0?FLinearColor(.8f,.82f,.8f):FLinearColor(.21f,.25f,.27f)));
   M->SetVectorParameterValue(TEXT("Sun color"),Colors[TimeOfDay]);FVector D=-FRotator(Pitch[TimeOfDay],TimeOfDay==2?30:-95,0).Vector();M->SetVectorParameterValue(TEXT("Light direction"),FLinearColor(D.X,D.Y,D.Z));
  }
 }
 const float Density[]={.006f,.012f,.065f,.025f};
 for(TActorIterator<AExponentialHeightFog> I(GetWorld());I;++I){I->GetComponent()->SetFogDensity(Density[Weather]);I->GetComponent()->SetFogInscatteringColor(TimeOfDay==3?FLinearColor(.025f,.045f,.08f):FLinearColor(.28f,.36f,.37f));}
 for(TActorIterator<ASkyLight> I(GetWorld());I;++I){I->GetLightComponent()->SetIntensity(TimeOfDay==3?.25f:.75f);I->GetLightComponent()->RecaptureSky();}
}
void ALurePawn::UpdateEnvironment(float Dt){
 if(AmbientAudio)AmbientAudio->SetVolumeMultiplier(Volume*(Weather==3?.8f:.5f));
 if(ReelAudio)ReelAudio->SetVolumeMultiplier(Reeling && !bMenuOpen?Volume*.55f:0);
 if(!Rain)return;Rain->SetVisibility(Weather==3);
 if(Weather==3){for(int i=0;i<130;++i){float X=FMath::Frac(i*.618f)*1000-500,Y=FMath::Frac(i*.414f)*1000-500,Z=FMath::Fmod(i*17.f-Clock*750,600.f);if(Z<0)Z+=600;FTransform T(FRotator(-12,0,0),GetActorLocation()+FVector(X,Y,Z),FVector(.002f,.002f,.26f));Rain->UpdateInstanceTransform(i,T,true,i==129,true);}}
}
void ALurePawn::RunSessionTest(){
 int Errors=0;auto Check=[&](bool B,const TCHAR* N){UE_LOG(LogTemp,Display,TEXT("LURE_SESSION %s: %s"),B?TEXT("PASS"):TEXT("FAIL"),N);if(!B)++Errors;};
 Check(SaveData!=nullptr,TEXT("session save object initialized"));
 MenuAction(TEXT("weather"));Check(Weather==1,TEXT("weather selection"));MenuAction(TEXT("time"));Check(TimeOfDay==1,TEXT("time selection"));
 MenuAction(TEXT("spot"));Check(Spot==1 && FMath::Abs(GetActorLocation().Y+1600)<1,TEXT("spot change moves player"));
 for(int i=0;i<100;++i)MenuAction(TEXT("sens+"));Check(Sensitivity<=.4f,TEXT("sensitivity capped"));
 for(int i=0;i<100;++i)MenuAction(TEXT("volume-"));Check(Volume==0,TEXT("volume floor"));
 ActiveFish=Fish[0];++Catches;RecordCatch();Check(SaveData->Journal.Num()==1 && SaveData->Journal[0].Weight>0,TEXT("catch journal records fish"));
 Phase=EFishingPhase::Fighting;ActiveFish=Fish[0];ToggleObserve();bMenuOpen=true;ResetCast();Check(!bObserve && Phase==EFishingPhase::Ready,TEXT("reset from paused fish camera returns to shore"));bMenuOpen=false;
 const FString Slot=TEXT("Wildwater_AutomatedTest");bool W=UGameplayStatics::SaveGameToSlot(SaveData,Slot,0);auto* Read=Cast<ULureSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));Check(W && Read && Read->Journal.Num()==1 && Read->BestWeight>0,TEXT("save and reload round trip with personal best"));UGameplayStatics::DeleteGameInSlot(Slot,0);
 UE_LOG(LogTemp,Display,TEXT("LURE_SESSION COMPLETE failures=%d"),Errors);FPlatformMisc::RequestExitWithStatus(false,Errors?1:0);
}


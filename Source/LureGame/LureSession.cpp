#include "LureWorld.h"
#include "CoveTerrain.h"
#include "CoveEnvironment.h"
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
#include "Engine/StaticMesh.h"
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
#include "Serialization/MemoryReader.h"
#include "Serialization/MemoryWriter.h"
#include "Serialization/ObjectAndNameAsStringProxyArchive.h"
#include "UObject/UnrealType.h"
namespace {
bool IsTesting(){return FParse::Param(FCommandLine::Get(),TEXT("LureSmokeTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureInputTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureSessionTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))||FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"))||FParse::Param(FCommandLine::Get(),TEXT("LureRigReview"))||FParse::Param(FCommandLine::Get(),TEXT("LureEncounterTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureEncounterCapture"))||FParse::Param(FCommandLine::Get(),TEXT("LurePopulationTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureShoreTest"))||FParse::Param(FCommandLine::Get(),TEXT("LureShoreCapture"));}
// Exercise the same tagged-property serialization as SaveGame, with the new
// field genuinely absent from the payload as it is in an older player save.
struct FLegacyFishingSaveArchive : FObjectAndNameAsStringProxyArchive {
 explicit FLegacyFishingSaveArchive(FArchive& Inner):FObjectAndNameAsStringProxyArchive(Inner,false){}
 virtual bool ShouldSkipProperty(const FProperty* Property) const override {
  if(Property && Property->GetFName()==GET_MEMBER_NAME_CHECKED(ULureSave,bFishingAssist)){bSkippedAssist=true;return true;}
  return FObjectAndNameAsStringProxyArchive::ShouldSkipProperty(Property);
 }
 mutable bool bSkippedAssist=false;
};
void RecoverCatchBests(ULureSave* Save){
 // Older saves have a journal but no per-species records or experience.
 for(const FCatchRecord& Entry:Save->Journal){
  if(Entry.Species.IsEmpty())continue;
  float& Best=Save->SpeciesBests.FindOrAdd(Entry.Species);
  Best=FMath::Max(Best,Entry.Weight);Save->BestWeight=FMath::Max(Save->BestWeight,Entry.Weight);
 }
}
}
FString ALurePawn::LureName() const {const TCHAR* N[]={TEXT("悬浮米诺"),TEXT("软虫"),TEXT("旋转亮片"),TEXT("水面波爬"),TEXT("铅头钩")};return N[LureType%5];}
FString ALurePawn::WeatherName() const {const TCHAR* N[]={TEXT("晴朗"),TEXT("阴天"),TEXT("薄雾"),TEXT("小雨")};return N[Weather%4];}
FString ALurePawn::TimeName() const {const TCHAR* N[]={TEXT("清晨 06:30"),TEXT("午后 14:00"),TEXT("黄昏 18:20"),TEXT("夜晚 21:00")};return N[TimeOfDay%4];}
FString ALurePawn::SpotName() const {const TCHAR* N[]={TEXT("沉木湾"),TEXT("芦苇浅滩"),TEXT("岩石岬角")};return N[Spot%3];}
void ALurePawn::SessionInit(){
 if(!IsTesting())SaveData=Cast<ULureSave>(UGameplayStatics::LoadGameFromSlot(TEXT("WildwaterV1"),0));
 if(!SaveData)SaveData=NewObject<ULureSave>(this);
 RecoverCatchBests(SaveData);
 Sensitivity=FMath::Clamp(SaveData->Sensitivity,.04f,.4f);Volume=FMath::Clamp(SaveData->Volume,0.f,1.f);Weather=FMath::Clamp(SaveData->Weather,0,3);TimeOfDay=FMath::Clamp(SaveData->TimeOfDay,0,3);Spot=FMath::Clamp(SaveData->Spot,0,2);Catches=SaveData->TotalCatches;{const float Y=Spot==0?0:(Spot==1?-1600:1600);SetActorLocation(FVector(-420,Y,Cove::Height(-420,Y)));}
 if(auto* Audio=LoadObject<USoundBase>(nullptr,TEXT("/Game/Audio/Ambient.Ambient")))AmbientAudio=UGameplayStatics::SpawnSound2D(this,Audio,Volume*.55f,1,0,nullptr,true,false);
 if(auto* Audio=LoadObject<USoundBase>(nullptr,TEXT("/Game/Audio/Reel.Reel"))){ReelAudio=UGameplayStatics::SpawnSound2D(this,Audio,0,1,0,nullptr,true,false);}
 if(auto* Audio=LoadObject<USoundBase>(nullptr,TEXT("/Game/Audio/DragRun.DragRun"))){DragAudio=UGameplayStatics::SpawnSound2D(this,Audio,0,1,0,nullptr,true,false);}
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
 FCatchRecord R;R.Species=ActiveFish->SpeciesName();R.Weight=ActiveFish->Weight;
 const UStaticMesh* BodyMesh=ActiveFish->Body->GetStaticMesh();
 R.Length=((BodyMesh?BodyMesh->GetBoundingBox().GetSize().X:40.f)+10.f)*ActiveFish->SizeFactor;
 R.Date=FDateTime::Now().ToString(TEXT("%Y-%m-%d %H:%M"));R.Lure=LureName();
 RecoverCatchBests(SaveData);
 const float* PreviousBest=SaveData->SpeciesBests.Find(R.Species);
 bNewSpecies=PreviousBest==nullptr;
 bPersonalBest=PreviousBest && R.Weight>*PreviousBest+.005f;
 R.HookQuality=FMath::Clamp(HookQuality,0.f,1.f);R.FightSeconds=FMath::Max(0.f,Fight.Time);
 const float Control=Fight.Time>0?FMath::Clamp(Fight.CleanSeconds/Fight.Time,0.f,1.f):0.f;
 const float Skill=R.HookQuality*.4f+Control*.6f;
 CatchGrade=Skill>=.88f?TEXT("S 级"):(Skill>=.7f?TEXT("A 级"):(Skill>=.45f?TEXT("B 级"):TEXT("C 级")));
 CatchScore=FMath::Max(0,FMath::RoundToInt(R.Weight*100+R.HookQuality*300+Control*400+FMath::Clamp(Fight.LineCondition,0.f,1.f)*100));
 CatchXP=50+CatchScore/15+(bNewSpecies?75:0)+(bPersonalBest?50:0);R.Score=CatchScore;
 SaveData->Experience+=CatchXP;SaveData->TotalCatches=Catches;
 SaveData->SpeciesBests.FindOrAdd(R.Species)=FMath::Max(PreviousBest?*PreviousBest:0.f,R.Weight);
 SaveData->BestWeight=FMath::Max(SaveData->BestWeight,R.Weight);
 SaveData->Journal.Insert(R,0);if(SaveData->Journal.Num()>100)SaveData->Journal.SetNum(100);
 LastCatch=FString::Printf(TEXT("%s  ·  %.2f kg  ·  %.0f cm"),*R.Species,R.Weight,R.Length);SaveSession();PlayCue(TEXT("Trophy"));
}
void ALurePawn::MenuAction(const FString& A){
 if(A==TEXT("play")){
  bMenuOpen=false;bStarted=true;Rig->SetVisibility(!bObserve,true);CaptureMouse();Notice=TEXT("看水面与竿线，听泄力声；Esc → 设置可开启钓鱼辅助。");SaveSession();
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
 else if(A==TEXT("fishing-assist")){
  // Return the underwater camera before disabling its entry permission.
  // A landed-fish close-up remains available in either mode.
  if(SaveData->bFishingAssist && bObserve && Phase!=EFishingPhase::Landed)ToggleObserve();
  SaveData->bFishingAssist=!SaveData->bFishingAssist;
  if(bMenuOpen)Rig->SetVisibility(false,true);
 }
 else if(A==TEXT("quality")){SaveData->Quality=(SaveData->Quality+1)%3;auto* Q=UGameUserSettings::GetGameUserSettings();Q->SetOverallScalabilityLevel(SaveData->Quality);Q->ApplyNonResolutionSettings();}
 else if(A==TEXT("fullscreen")){SaveData->bFullscreen=!SaveData->bFullscreen;auto* Q=UGameUserSettings::GetGameUserSettings();Q->SetFullscreenMode(SaveData->bFullscreen?EWindowMode::WindowedFullscreen:EWindowMode::Windowed);Q->ApplyResolutionSettings(false);}
 SaveSession();
}
void ALurePawn::ApplyEnvironment(){
 // Clear, overcast, mist and light rain use distinct surface conditions.
 const float WaveStrength[]={1.f,1.4f,.35f,2.2f};
 const float WaterRoughness[]={.12f,.15f,.08f,.22f};
 for(TActorIterator<ACoveEnvironment> I(GetWorld());I;++I){
  auto* Material=Cast<UMaterialInstanceDynamic>(I->Water->GetMaterial(0));
  if(!Material)Material=I->Water->CreateDynamicMaterialInstance(0);
  if(Material){
   Material->SetScalarParameterValue(TEXT("WaveStrength"),WaveStrength[Weather]);
   Material->SetScalarParameterValue(TEXT("WaterRoughness"),WaterRoughness[Weather]);
  }
 }
 const float Pitch[]={-15.f,-58.f,-8.f,-25.f};const float Lux[]={30000.f,55000.f,12000.f,.12f};
 const FLinearColor Colors[]={FLinearColor(1,.94f,.84f),FLinearColor(1,.98f,.95f),FLinearColor(1,.5f,.23f),FLinearColor(.38f,.52f,1)};
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
 if(DragAudio && bMenuOpen)DragAudio->SetVolumeMultiplier(0);
 if(!Rain)return;Rain->SetVisibility(Weather==3);
 if(Weather==3){for(int i=0;i<130;++i){float X=FMath::Frac(i*.618f)*1000-500,Y=FMath::Frac(i*.414f)*1000-500,Z=FMath::Fmod(i*17.f-Clock*750,600.f);if(Z<0)Z+=600;FTransform T(FRotator(-12,0,0),GetActorLocation()+FVector(X,Y,Z),FVector(.002f,.002f,.26f));Rain->UpdateInstanceTransform(i,T,true,i==129,true);}}
}
void ALurePawn::RunSessionTest(){
 int Errors=0;auto Check=[&](bool B,const TCHAR* N){UE_LOG(LogTemp,Display,TEXT("LURE_SESSION %s: %s"),B?TEXT("PASS"):TEXT("FAIL"),N);if(!B)++Errors;};
 Check(SaveData!=nullptr,TEXT("session save object initialized"));
 Check(SaveData && !SaveData->bFishingAssist,TEXT("new session defaults to shore fishing without assist"));
 MenuAction(TEXT("fishing-assist"));Check(SaveData->bFishingAssist,TEXT("fishing assist can be enabled from settings"));
 MenuAction(TEXT("weather"));Check(Weather==1,TEXT("weather selection"));MenuAction(TEXT("time"));Check(TimeOfDay==1,TEXT("time selection"));
 MenuAction(TEXT("spot"));Check(Spot==1 && FMath::Abs(GetActorLocation().Y+1600)<1,TEXT("spot change moves player"));
 for(int i=0;i<100;++i)MenuAction(TEXT("sens+"));Check(Sensitivity<=.4f,TEXT("sensitivity capped"));
 for(int i=0;i<100;++i)MenuAction(TEXT("volume-"));Check(Volume==0,TEXT("volume floor"));
 ActiveFish=Fish[0];HookQuality=.9f;Fight.Time=42;Fight.CleanSeconds=33.6f;Fight.LineCondition=.85f;++Catches;RecordCatch();
 Check(SaveData->Journal.Num()==1 && SaveData->Journal[0].Weight>0,TEXT("catch journal records fish"));
 Check(bNewSpecies && !bPersonalBest && CatchXP>0 && CatchScore>0,TEXT("first species awards discovery and experience"));
 const int32 FirstXP=SaveData->Experience;const float FirstWeight=ActiveFish->Weight;
 SaveData->SpeciesBests.Empty();ActiveFish->Weight=FirstWeight*1.25f;++Catches;RecordCatch();
 Check(!bNewSpecies && bPersonalBest && SaveData->Experience>FirstXP,TEXT("legacy journal retains discovery and recognizes a heavier personal best"));
 ++Catches;RecordCatch();
 Check(!bNewSpecies && !bPersonalBest,TEXT("equal weight cannot repeatedly claim a personal best"));
 ActiveFish->Weight=FirstWeight;
 Phase=EFishingPhase::Fighting;ActiveFish=Fish[0];ToggleObserve();
 Check(bObserve,TEXT("enabled assist permits underwater observation"));
 bMenuOpen=true;MenuAction(TEXT("fishing-assist"));
 Check(!SaveData->bFishingAssist && !bObserve && bMenuOpen,TEXT("disabling assist returns underwater view to shore without closing settings"));
 bMenuOpen=false;ToggleObserve();Check(!bObserve,TEXT("shore mode cannot enter underwater observation"));
 MenuAction(TEXT("fishing-assist"));ToggleObserve();bMenuOpen=true;ResetCast();Check(!bObserve && Phase==EFishingPhase::Ready,TEXT("reset from paused fish camera returns to shore"));bMenuOpen=false;
 const FString Slot=TEXT("Wildwater_AutomatedTest");bool W=UGameplayStatics::SaveGameToSlot(SaveData,Slot,0);auto* Read=Cast<ULureSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
 Check(W && Read && Read->Journal.Num()==3 && Read->BestWeight>0,TEXT("save and reload round trip with personal best"));
 Check(W && Read && Read->bFishingAssist,TEXT("enabled fishing assist survives save and reload"));
 if(Read && Read->Journal.Num()==3){
  const FCatchRecord& Latest=Read->Journal[0];
  Check(Latest.Score==CatchScore && FMath::IsNearlyEqual(Latest.HookQuality,.9f) && FMath::IsNearlyEqual(Latest.FightSeconds,42.f),TEXT("catch skill and duration survive reload"));
  Check(Read->Experience==SaveData->Experience && Read->TotalCatches==Catches && FMath::IsNearlyEqual(Read->SpeciesBests.FindRef(Latest.Species),FirstWeight*1.25f),TEXT("experience and species best survive reload"));
 }
 // Serialize a legacy payload that contains the catch journal but omits the
 // assist property. Loading it must retain the new class's false default.
 TArray<uint8> LegacyBytes;bool bOmittedAssist=false;
 {FMemoryWriter Writer(LegacyBytes,true);FLegacyFishingSaveArchive Archive(Writer);SaveData->Serialize(Archive);bOmittedAssist=Archive.bSkippedAssist;}
 ULureSave* Legacy=NewObject<ULureSave>(this);
 {FMemoryReader Reader(LegacyBytes,true);FObjectAndNameAsStringProxyArchive Archive(Reader,true);Legacy->Serialize(Archive);}
 Check(bOmittedAssist && !Legacy->bFishingAssist && Legacy->Journal.Num()==SaveData->Journal.Num(),TEXT("legacy save without assist field loads catch history and defaults assist off"));
 SaveData->bFishingAssist=false;
 const bool WOff=UGameplayStatics::SaveGameToSlot(SaveData,Slot,0);
 Read=Cast<ULureSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
 Check(WOff && Read && !Read->bFishingAssist,TEXT("disabled fishing assist survives save and reload"));
 UGameplayStatics::DeleteGameInSlot(Slot,0);
 UE_LOG(LogTemp,Display,TEXT("LURE_SESSION COMPLETE failures=%d"),Errors);FPlatformMisc::RequestExitWithStatus(false,Errors?1:0);
}


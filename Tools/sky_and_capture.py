from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('GetWorld()->SpawnActor<ASkyAtmosphere>();','''GetWorld()->SpawnActor<ASkyAtmosphere>();
 auto* Dome=GetWorld()->SpawnActor<AStaticMeshActor>();Dome->Tags.Add(TEXT("SkyDome"));Dome->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);Dome->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/EngineSky/SM_SkySphere.SM_SkySphere")));Dome->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Dome->GetStaticMeshComponent()->SetCastShadow(false);Dome->SetActorScale3D(FVector(400));
 auto* SkyMat=UMaterialInstanceDynamic::Create(LoadObject<UMaterialInterface>(nullptr,TEXT("/Engine/EngineSky/M_Sky_Panning_Clouds2.M_Sky_Panning_Clouds2")),Dome);Dome->GetStaticMeshComponent()->SetMaterial(0,SkyMat);
''')
s=s.replace('FVector Eye=Focus+FVector(90,-145,55);','FVector Eye=Focus+FVector(90,-145,55);if(Phase!=EFishingPhase::Landed)Eye.Z=FMath::Min(Focus.Z+25,-30.f);')
s=s.replace(' if(bMenuOpen){Reeling=false;', ''' if(FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"))){
  auto At=[&](float T){return Clock>T && Clock-Dt<=T;};
  if(At(10))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Menu.png"),true,false);
  if(At(11))MenuPage=1;
  if(At(13))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Settings.png"),true,false);
  if(Clock>15)FPlatformMisc::RequestExit(false);
 }
 if(bMenuOpen){Reeling=false;''')
p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureSession.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('#include "Engine/DirectionalLight.h"','#include "Engine/DirectionalLight.h"\n#include "Engine/StaticMeshActor.h"\n#include "Materials/MaterialInstanceDynamic.h"')
s=s.replace('||FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))','||FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))||FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"))')
s=s.replace('if(!IsTesting()){\n  bMenuOpen=true;', 'if(!IsTesting() || FParse::Param(FCommandLine::Get(),TEXT("LureMenuCapture"))){\n  bMenuOpen=true;')
s=s.replace('const float Density[]={', '''for(TActorIterator<AStaticMeshActor> I(GetWorld());I;++I)if(I->Tags.Contains(TEXT("SkyDome"))){
  if(auto* M=Cast<UMaterialInstanceDynamic>(I->GetStaticMeshComponent()->GetMaterial(0))){
   bool Night=TimeOfDay==3;M->SetScalarParameterValue(TEXT("Cloud speed"),Weather==3?1.f:.2f);M->SetScalarParameterValue(TEXT("Cloud opacity"),Weather==0?.35f:1.5f);M->SetScalarParameterValue(TEXT("Stars brightness"),Night?1.f:0.f);M->SetScalarParameterValue(TEXT("Sun brightness"),Night?.1f:15.f);M->SetScalarParameterValue(TEXT("Sun height"),.3f);M->SetScalarParameterValue(TEXT("Sun Radius"),.015f);
   M->SetVectorParameterValue(TEXT("Overall Color"),FLinearColor::White);
   M->SetVectorParameterValue(TEXT("Zenith Color"),Night?FLinearColor(.001f,.003f,.015f):FLinearColor(.045f,.14f,.27f));
   M->SetVectorParameterValue(TEXT("Horizon color"),Night?FLinearColor(.012f,.02f,.04f):(TimeOfDay==2?FLinearColor(.55f,.23f,.11f):FLinearColor(.48f,.6f,.62f)));
   M->SetVectorParameterValue(TEXT("Cloud color"),Night?FLinearColor(.015f,.024f,.04f):(Weather==0?FLinearColor(.8f,.82f,.8f):FLinearColor(.21f,.25f,.27f)));
   M->SetVectorParameterValue(TEXT("Sun color"),Colors[TimeOfDay]);FVector D=-FRotator(Pitch[TimeOfDay],TimeOfDay==2?30:-28,0).Vector();M->SetVectorParameterValue(TEXT("Light direction"),FLinearColor(D.X,D.Y,D.Z));
  }
 }
 const float Density[]={''')
p.write_text(s,encoding='utf-8')

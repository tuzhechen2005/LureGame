from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('#include "Camera/CameraComponent.h"','#include "Camera/CameraComponent.h"\n#include "Camera/PlayerCameraManager.h"\n#include "Components/InstancedStaticMeshComponent.h"')
a=s.index(' Place(GetWorld(),TEXT("Cube"),FVector(-800');b=s.index('\n}\nvoid ALureHUD::DrawHUD()',a)
s=s[:a]+''' auto* Shore=Place(GetWorld(),TEXT("Cube"),FVector(-1800,0,-70),FVector(36,180,2.8f),FLinearColor(.12f,.14f,.06f));
 Shore->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
 auto* Bed=Place(GetWorld(),TEXT("Cube"),FVector(3500,0,-440),FVector(70,100,1),FLinearColor(.14f,.17f,.095f));
 Bed->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
 auto* Water=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(0,-5000,0),FRotator::ZeroRotator);
 Water->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
 Water->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_WaterGrid.SM_WaterGrid")));
 Water->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_LakeWater.M_LakeWater")));
 Water->SetActorScale3D(FVector(70,100,1));Water->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 auto Instances=[&](const TCHAR* Name,UStaticMesh* M,FLinearColor C){
  auto* A=GetWorld()->SpawnActor<AActor>();auto* I=NewObject<UInstancedStaticMeshComponent>(A,Name);A->SetRootComponent(I);I->SetStaticMesh(M);I->SetCollisionEnabled(ECollisionEnabled::NoCollision);I->RegisterComponent();Tint(I,C);return I;
 };
 auto* Rocks=Instances(TEXT("Rocks"),LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Rock.SM_Rock")),FLinearColor(.13f,.145f,.12f));
 auto* Trunks=Instances(TEXT("Trunks"),Shape(TEXT("Cylinder")),FLinearColor(.08f,.048f,.023f));
 auto* Crowns=Instances(TEXT("Crowns"),Shape(TEXT("Cone")),FLinearColor(.025f,.085f,.038f));
 FRandomStream Rng(712);
 for(int i=0;i<100;++i){float Y=Rng.FRandRange(-5000,5000);FVector Pos(Rng.FRandRange(-70,120),Y,Rng.FRandRange(-50,0));Rocks->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),Pos,FVector(Rng.FRandRange(.5f,1.6f),Rng.FRandRange(.7f,2),Rng.FRandRange(.5f,1))),true);}
 for(int i=0;i<12;++i)Rocks->AddInstance(FTransform(FRotator(0,i*63,0),FVector(1650+i*65,850+FMath::Sin(i*2.f)*130,-50),FVector(1.2f,1.1f,1)),true);
 auto* Log=Place(GetWorld(),TEXT("Cylinder"),FVector(2150,700,0),FVector(.25f,.25f,5),FLinearColor(.09f,.045f,.019f));Log->SetActorRotation(FRotator(83,30,0));
 for(int i=0;i<160;++i){
  const bool Far=i>60;const float X=Far?Rng.FRandRange(6800,7700):Rng.FRandRange(-2600,-1450),Y=Rng.FRandRange(-5200,5200),H=Rng.FRandRange(500,1050);
  Trunks->AddInstance(FTransform(FRotator::ZeroRotator,FVector(X,Y,H*.4f),FVector(.25f,.25f,H/100)),true);
  for(int k=0;k<5;++k){float S=(1-k*.15f)*Rng.FRandRange(2.5f,3.5f);Crowns->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),FVector(X,Y,H*.45f+k*H*.11f),FVector(S,S,H/230)),true);}
 }
 for(int i=0;i<30;++i)Rocks->AddInstance(FTransform(FRotator(0,i*39,0),FVector(7000,Rng.FRandRange(-6500,6500),-70),FVector(Rng.FRandRange(3,8),Rng.FRandRange(4,8),Rng.FRandRange(3,6))),true);
 // Reeds at the waterline, instanced to keep draw calls low.
 auto* Reeds=Instances(TEXT("Reeds"),Shape(TEXT("Cylinder")),FLinearColor(.13f,.18f,.04f));
 for(int i=0;i<480;++i){float Y=Rng.FRandRange(-4500,4500);if(FMath::Abs(Y)<350)continue;float H=Rng.FRandRange(65,135);Reeds->AddInstance(FTransform(FRotator(Rng.FRandRange(-12,12),Rng.FRandRange(0,360),0),FVector(Rng.FRandRange(-40,160),Y,H*.4f),FVector(.012f,.012f,H/100)),true);}
 auto* Sun=GetWorld()->SpawnActor<ADirectionalLight>(FVector(0,0,2000),FRotator(-24,-28,0));Sun->GetLightComponent()->SetIntensity(3.f);Sun->GetLightComponent()->SetLightColor(FLinearColor(1,.88f,.7f));
 Cast<UDirectionalLightComponent>(Sun->GetLightComponent())->SetAtmosphereSunLight(true);
 GetWorld()->SpawnActor<ASkyAtmosphere>();
 auto* Sky=GetWorld()->SpawnActor<ASkyLight>();Sky->GetLightComponent()->SetMobility(EComponentMobility::Movable);Sky->GetLightComponent()->SetIntensity(.8f);Sky->GetLightComponent()->RecaptureSky();
 auto* Fog=GetWorld()->SpawnActor<AExponentialHeightFog>();Fog->GetComponent()->SetFogDensity(.008f);Fog->GetComponent()->SetFogHeightFalloff(.16f);Fog->GetComponent()->SetFogInscatteringColor(FLinearColor(.3f,.4f,.42f));
 auto* Post=GetWorld()->SpawnActor<APostProcessVolume>();Post->bUnbound=true;Post->Settings.bOverride_AutoExposureBias=true;Post->Settings.AutoExposureBias=-.5f;
 Post->Settings.bOverride_MotionBlurAmount=true;Post->Settings.MotionBlurAmount=0;
''' + s[b:]
p.write_text(s,encoding='utf-8')

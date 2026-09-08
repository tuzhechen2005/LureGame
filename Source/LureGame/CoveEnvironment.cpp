#include "CoveEnvironment.h"
#include "Components/StaticMeshComponent.h"
#include "Components/HierarchicalInstancedStaticMeshComponent.h"
ACoveEnvironment::ACoveEnvironment() {
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
 Terrain=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Terrain"));Terrain->SetupAttachment(RootComponent);
 Terrain->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_CoveTerrain.SM_CoveTerrain")));
 Terrain->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
 Terrain->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Water=CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Water"));Water->SetupAttachment(RootComponent);
 Water->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_WaterGrid.SM_WaterGrid")));
 Water->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_LakeWater.M_LakeWater")));
 Water->SetRelativeLocation(FVector(0,6500,0));Water->SetRelativeScale3D(FVector(70,130,1));Water->SetCastShadow(false);Water->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 const TCHAR* Names[]={TEXT("SM_Birch"),TEXT("SM_Grass"),TEXT("SM_Rock"),TEXT("SM_ScanRock1"),TEXT("SM_ScanRock2"),TEXT("SM_ScanRock3"),TEXT("SM_ScanRock4"),TEXT("SM_ScanRock5")};
 for(const TCHAR* Name:Names){
  auto* I=CreateDefaultSubobject<UHierarchicalInstancedStaticMeshComponent>(Name);I->SetupAttachment(RootComponent);
  const FString Path=FString::Printf(TEXT("/Game/LureArt/%s.%s"),Name,Name);I->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*Path));
  I->SetCollisionEnabled(ECollisionEnabled::NoCollision);Groups.Add(I);
 }
}

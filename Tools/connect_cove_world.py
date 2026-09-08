from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('#include "LureWorld.h"','#include "LureWorld.h"\n#include "CoveEnvironment.h"\n#include "CoveTerrain.h"')
s=s.replace('/Game/LureArt/SM_LeftArm.SM_LeftArm','/Game/LureArt/SM_AnatomicalLeft.SM_AnatomicalLeft').replace('/Game/LureArt/SM_RightArm.SM_RightArm','/Game/LureArt/SM_AnatomicalRight.SM_AnatomicalRight')
s=s.replace('PC->SetControlRotation(FRotator(-8,0,0))','PC->SetControlRotation(FRotator(-7,-40,0))')
s=s.replace('P.Y=FMath::Clamp(P.Y,-1900.0f,1900.0f); SetActorLocation(P);','P.Y=FMath::Clamp(P.Y,-1900.0f,1900.0f); P.Z=Cove::Height(P.X,P.Y); SetActorLocation(P);')
start=s.index('void ALureGameMode::BeginPlay(){');pos=s.index('Super::BeginPlay();',start)+len('Super::BeginPlay();')
s=s[:pos]+'\n for(TActorIterator<ACoveEnvironment> It(GetWorld());It;++It)return;\n'+s[pos:]
p.write_text(s,encoding='utf-8-sig')
p=Path('D:/LureGame/Source/LureGame/LureSession.cpp');s=p.read_text(encoding='utf-8-sig').replace('#include "LureWorld.h"','#include "LureWorld.h"\n#include "CoveTerrain.h"')
s=s.replace('SetActorLocation(FVector(-420,Spot==0?0:(Spot==1?-1600:1600),70));','{const float Y=Spot==0?0:(Spot==1?-1600:1600);SetActorLocation(FVector(-420,Y,Cove::Height(-420,Y)));}')
s=s.replace('const float Lux[]={3.f,5.f,2.f,.16f}','const float Lux[]={30000.f,55000.f,12000.f,.12f}')
# The first authored shot uses lateral afternoon sunlight; preset time labels remain accurate.
s=s.replace('TimeOfDay==2?30:-28','TimeOfDay==2?30:-95')
s=s.replace('Spot==1?18:(Spot==2?-18:0)','Spot==1?-20:(Spot==2?-55:-40)')
s=s.replace('void ALurePawn::SaveSession(){','void ALurePawn::SaveSession(){')
needle='void ALurePawn::SaveSession()'
pos=s.index(needle);before=s[:pos];last=before.rfind('\n}')
before=before[:last]+'\n ApplyEnvironment();'+before[last:];s=before+s[pos:]
p.write_text(s,encoding='utf-8-sig')
p=Path('D:/LureGame/Source/LureGame/LureSave.h');s=p.read_text(encoding='utf-8-sig').replace('Quality=1','Quality=2');p.write_text(s,encoding='utf-8-sig')
print('COVE_WORLD_CONNECTED')

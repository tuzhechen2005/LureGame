from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
key=' auto* Bed=Place'
i=s.index(key)
s=s[:i]+''' auto* FarShore=GetWorld()->SpawnActor<AStaticMeshActor>(FVector(7000,0,0),FRotator(0,180,0));
 FarShore->GetStaticMeshComponent()->SetMobility(EComponentMobility::Movable);
 FarShore->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Bank.SM_Bank")));
 FarShore->GetStaticMeshComponent()->SetMaterial(0,LoadObject<UMaterialInterface>(nullptr,TEXT("/Game/LureArt/M_Shore.M_Shore")));
''' +s[i:]
s=s.replace('for(int i=0;i<160;++i)', 'for(int i=0;i<240;++i)').replace('Rng.FRandRange(6800,7700)','Rng.FRandRange(7250,10100)').replace('H=Rng.FRandRange(500,1050)','H=Rng.FRandRange(650,1600)').replace('Far?-50:65','Far?50:65')
s=s.replace('Sun->GetLightComponent()->SetIntensity(3.f);','Sun->GetLightComponent()->SetMobility(EComponentMobility::Movable);Sun->GetLightComponent()->SetIntensity(3.f);')
p.write_text(s,encoding='utf-8-sig')
credit=Path('D:/LureGame/Docs/Credits.md');credit.write_text(credit.read_text()+'\n- Shore ground: https://polyhaven.com/a/brown_mud_leaves_01 (CC0).\n')

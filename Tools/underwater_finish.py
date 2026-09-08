from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('Water->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);','Water->GetStaticMeshComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);Water->GetStaticMeshComponent()->SetCastShadow(false);')
s=s.replace('FVector Eye=Focus+FVector(90,-145,55);','FVector Eye=Focus+FVector(-90,145,55);')
s=s.replace('bObserve=!bObserve;Camera->bUsePawnControlRotation=!bObserve;', '''bObserve=!bObserve;Camera->bUsePawnControlRotation=!bObserve;
 if(bObserve && Phase!=EFishingPhase::Landed){for(TActorIterator<AExponentialHeightFog> I(GetWorld());I;++I){I->GetComponent()->SetFogDensity(.16f);I->GetComponent()->SetFogHeightFalloff(.001f);I->GetComponent()->SetFogInscatteringColor(FLinearColor(.015f,.095f,.075f));}}
 else {ApplyEnvironment();for(TActorIterator<AExponentialHeightFog> I(GetWorld());I;++I)I->GetComponent()->SetFogHeightFalloff(.16f);}''')
s=s.replace('if(Clock>44)FPlatformMisc::RequestExit(false);', '''if(At(44)){ResetCast();Weather=3;ApplyEnvironment();}
  if(At(49))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Rain.png"),true,false);
  if(At(50)){Weather=0;TimeOfDay=2;ApplyEnvironment();}
  if(At(55))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Sunset.png"),true,false);
  if(At(56)){TimeOfDay=3;ApplyEnvironment();}
  if(At(61))FScreenshotRequest::RequestScreenshot(TEXT("D:/LureGame/Saved/Night.png"),true,false);
  if(Clock>64)FPlatformMisc::RequestExit(false);''')
p.write_text(s,encoding='utf-8')

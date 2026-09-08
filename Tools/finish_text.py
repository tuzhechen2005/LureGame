from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
translations={'Cast released':'拟饵已抛出','HOOK SET! Keep tension in the green zone.':'刺鱼成功！保持张力，鱼发力时适当松线。','Twitch ... pause to let the lure settle.':'轻抽一下，停顿，等待拟饵下沉。','Aim over the water. Hold LMB, release to cast.':'向湖面瞄准，按住左键蓄力，松开抛投。','Missed the lake. Aim toward the open water.':'落点在岸上，请朝开阔水面抛投。','Splash! Hold RMB to retrieve; Space to twitch.':'拟饵入水。右键收线，空格轻抽。','Lure recovered. Try a new cast.':'拟饵已收回，可以再次抛投。','Missed bite. The fish is retreating; try another pause.':'错过咬口，鱼暂时逃开了。换个节奏再试试。','Line broke! Lower drag or stop reeling during surges.':'断线了！鱼发力时请松开收线，或降低泄力。','BASS LANDED! Press V to inspect, R to release.':'成功上鱼！V 查看，R 放流。','Fish escaped beyond your line capacity.':'鱼游出了可控距离。下次注意及时回收鱼线。','BITE! Press SPACE now!':'咬口！立即按空格刺鱼！'}
for a,b in translations.items():s=s.replace('TEXT("'+a+'")','TEXT("'+b+'")')
s=s.replace('Notice.Contains(TEXT("broke"))','Notice.Contains(TEXT("断线"))')
s=s.replace('bMenuOpen=true;MenuPage=0;Reeling=false;', 'if(Phase==EFishingPhase::Charging)ResetCast();\n bMenuOpen=true;MenuPage=0;Reeling=false;')
s=s.replace('void ALurePawn::ToggleObserve(){','void ALurePawn::ToggleObserve(){\n if(bMenuOpen)return;')
p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureHUD.cpp');s=p.read_text(encoding='utf-8-sig').replace('if(P->Phase==EFishingPhase::Ready)Text(TEXT("按住左键蓄力，松开抛投"),490,484,19,White);','if(P->Phase==EFishingPhase::Ready)Text(P->Notice,410,484,18,White);');p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureSession.cpp');s=p.read_text(encoding='utf-8-sig').replace('Catches=SaveData->TotalCatches;','Catches=SaveData->TotalCatches;SetActorLocation(FVector(-420,Spot==0?0:(Spot==1?-1600:1600),70));');p.write_text(s,encoding='utf-8')

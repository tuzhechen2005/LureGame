from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureSave.h');s=p.read_text(encoding='utf-8-sig').replace('UPROPERTY() int32 TotalCatches=0;','UPROPERTY() int32 TotalCatches=0;\n UPROPERTY() float BestWeight=0;');p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureSession.cpp');s=p.read_text(encoding='utf-8-sig').replace('SaveData->Journal.Insert(R,0);','SaveData->BestWeight=FMath::Max(SaveData->BestWeight,R.Weight);\n SaveData->Journal.Insert(R,0);')
s=s.replace('Check(W && Read && Read->Journal.Num()==1,TEXT("save and reload round trip"))','Check(W && Read && Read->Journal.Num()==1 && Read->BestWeight>0,TEXT("save and reload round trip with personal best"))')
s=s.replace('const FString Slot=TEXT("Wildwater_AutomatedTest");','''Phase=EFishingPhase::Fighting;ActiveFish=Fish[0];ToggleObserve();bMenuOpen=true;ResetCast();Check(!bObserve && Phase==EFishingPhase::Ready,TEXT("reset from paused fish camera returns to shore"));bMenuOpen=false;
 const FString Slot=TEXT("Wildwater_AutomatedTest");''')
p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureHUD.cpp');s=p.read_text(encoding='utf-8-sig').replace('Text(TEXT("Windows 单机版 1.0  ·  本地自动保存")','Text(FString::Printf(TEXT("个人纪录  %.2f kg"),P->SaveData->BestWeight),560,478,18,Accent);\n   Text(TEXT("Windows 单机版 1.0  ·  本地自动保存")');p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig').replace('void ALurePawn::ToggleObserve(){\n if(bMenuOpen)return;','void ALurePawn::ToggleObserve(){')
s=s.replace('#include "HAL/PlatformMisc.h"','#include "HAL/PlatformMisc.h"\n#include "HAL/PlatformMemory.h"')
s=s.replace('if(FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))) {','if(FParse::Param(FCommandLine::Get(),TEXT("LureCapture"))) {\n  static TArray<float> FrameSamples;if(Clock>10)FrameSamples.Add(Dt);')
s=s.replace('if(Clock>64)FPlatformMisc::RequestExit(false);','''if(Clock>64){float Sum=0;for(float V:FrameSamples)Sum+=V;FrameSamples.Sort();int Count=FrameSamples.Num();if(Count)UE_LOG(LogTemp,Display,TEXT("LURE_PERF frames=%d avg_ms=%.2f p95_ms=%.2f working_set_mb=%.0f offscreen_capture=true"),Count,Sum/Count*1000,FrameSamples[FMath::Min(Count-1,int(Count*.95f))]*1000,FPlatformMemory::GetStats().UsedPhysical/1048576.0);FPlatformMisc::RequestExit(false);}''')
p.write_text(s,encoding='utf-8')

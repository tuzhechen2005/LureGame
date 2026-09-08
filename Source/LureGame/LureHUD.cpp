#include "LureWorld.h"
#include "LureSave.h"
#include "Engine/Canvas.h"
#include "CanvasItem.h"
#include "Engine/Font.h"
#include "Fonts/CompositeFont.h"
#include "GameFramework/PlayerController.h"
#include "Misc/Paths.h"
#include "InputCoreTypes.h"
void ALureHUD::DrawHUD(){
 Super::DrawHUD();auto* P=Cast<ALurePawn>(GetOwningPawn());if(!P||!Canvas)return;
 if(!ChineseFont){ChineseFont=NewObject<UFont>(this);ChineseFont->FontCacheType=EFontCacheType::Runtime;ChineseFont->LegacyFontSize=20;ChineseFont->GetMutableInternalCompositeFont().DefaultTypeface.Fonts.Add(FTypefaceEntry(TEXT("Regular"),FPaths::ProjectContentDir()/TEXT("UI/Chinese.ttf"),EFontHinting::Default,EFontLoadingPolicy::LazyLoad));}
 const float S=FMath::Min(Canvas->SizeX/1280.f,Canvas->SizeY/720.f);const float OX=(Canvas->SizeX-1280*S)/2,OY=(Canvas->SizeY-720*S)/2;
 const FLinearColor White(.9f,.94f,.9f),Muted(.53f,.67f,.64f),Accent(.35f,.8f,.67f),Panel(.012f,.025f,.024f,.9f);
 auto Rect=[&](float X,float Y,float W,float H,FLinearColor C){DrawRect(C,OX+X*S,OY+Y*S,W*S,H*S);};
 auto Text=[&](const FString& T,float X,float Y,float Size,FLinearColor C){FCanvasTextItem Item(FVector2D(OX+X*S,OY+Y*S),FText::FromString(T),FSlateFontInfo(ChineseFont,FMath::RoundToInt(Size*S*.75f)),C);Canvas->DrawItem(Item);};
 auto* PC=GetOwningPlayerController();float MX=0,MY=0;PC->GetMousePosition(MX,MY);MX=(MX-OX)/S;MY=(MY-OY)/S;
 const bool Click=PC->WasInputKeyJustPressed(EKeys::LeftMouseButton);
 auto Button=[&](FString Label,float X,float Y,float W,FString Action){bool Hover=MX>=X&&MX<=X+W&&MY>=Y&&MY<=Y+44;Rect(X,Y,W,44,Hover?FLinearColor(.10f,.26f,.22f,.97f):FLinearColor(.04f,.09f,.075f,.95f));Text(Label,X+16,Y+10,18,Hover?Accent:White);if(Hover&&Click)P->MenuAction(Action);};
 if(P->bMenuOpen){
  Rect(0,0,1280,720,FLinearColor(.006f,.018f,.018f,.55f));Rect(40,40,1200,640,Panel);
  Text(TEXT("野 水"),80,64,54,White);Text(TEXT("W I L D W A T E R   /   L U R E"),83,131,16,Accent);
  Rect(80,176,1120,1,FLinearColor(.15f,.3f,.25f));
  if(P->MenuPage==0){
   Text(P->bStarted?TEXT("慢一点，让水面告诉你答案。"):TEXT("读懂水域，感受每一次咬口。"),80,202,22,Muted);
   Button(P->bStarted?TEXT("继续钓鱼"):TEXT("开始钓鱼"),80,259,320,TEXT("play"));
   Button(TEXT("鱼获手册"),80,316,320,TEXT("journal"));Button(TEXT("环境与设置"),80,373,320,TEXT("settings"));Button(TEXT("操作指南"),80,430,320,TEXT("help"));Button(TEXT("保存并退出"),80,487,320,TEXT("quit"));
   Text(TEXT("本次出钓"),560,227,26,White);Text(P->SpotName(),560,277,32,Accent);Text(P->WeatherName()+TEXT("  /  ")+P->TimeName(),560,326,22,Muted);
   Text(TEXT("4 种淡水鱼 · 5 种拟饵 · 3 处岸钓标点"),560,398,20,White);
   Text(FString::Printf(TEXT("累计上鱼 %d 尾  |  所有鱼获均可放流"),P->Catches),560,439,18,Muted);
   Text(FString::Printf(TEXT("个人纪录  %.2f kg"),P->SaveData->BestWeight),560,478,18,Accent);
   Text(TEXT("Windows 单机版 1.0  ·  本地自动保存"),80,624,15,Muted);
  }else if(P->MenuPage==1){
   Text(TEXT("环境与设置"),80,204,28,White);
   Button(TEXT("天气：")+P->WeatherName(),80,260,490,TEXT("weather"));Button(TEXT("时段：")+P->TimeName(),80,316,490,TEXT("time"));Button(TEXT("标点：")+P->SpotName()+TEXT("（切换时收竿）"),80,372,490,TEXT("spot"));
   Text(FString::Printf(TEXT("鼠标灵敏度  %.2f"),P->Sensitivity),680,267,20,White);Button(TEXT("－"),990,257,64,TEXT("sens-"));Button(TEXT("＋"),1066,257,64,TEXT("sens+"));
   Text(FString::Printf(TEXT("声音音量  %.0f%%"),P->Volume*100),680,327,20,White);Button(TEXT("－"),990,317,64,TEXT("volume-"));Button(TEXT("＋"),1066,317,64,TEXT("volume+"));
   const TCHAR* Quality[]={TEXT("性能"),TEXT("均衡"),TEXT("精细")};Button(FString(TEXT("画质："))+Quality[P->SaveData->Quality],680,377,450,TEXT("quality"));Button(P->SaveData->bFullscreen?TEXT("显示：无边框全屏"):TEXT("显示：窗口"),680,433,450,TEXT("fullscreen"));
   Text(TEXT("天气与时段会影响鱼的活跃度。笔记本建议先使用“均衡”。"),80,517,18,Muted);Button(TEXT("返回"),80,584,200,TEXT("back"));
  }else if(P->MenuPage==2){
   Text(TEXT("鱼获手册"),80,202,28,White);Text(TEXT("最近 8 次上鱼 / 本地保留最近 100 条记录"),400,209,17,Muted);
   if(P->SaveData->Journal.IsEmpty())Text(TEXT("还没有鱼获。到沉木附近试一试抽停米诺。"),80,295,22,Muted);
   for(int i=0;i<FMath::Min(8,P->SaveData->Journal.Num());++i){auto& R=P->SaveData->Journal[i];float Y=262+i*36;Text(R.Species,80,Y,19,White);Text(FString::Printf(TEXT("%.2f kg  /  %.0f cm"),R.Weight,R.Length),325,Y,18,Accent);Text(R.Lure,610,Y,18,Muted);Text(R.Date,870,Y,17,Muted);}
   Button(TEXT("返回"),80,596,200,TEXT("back"));
  }else{
   Text(TEXT("操作指南"),80,202,28,White);
   const TCHAR* H[]={TEXT("W A S D 移动，鼠标自由瞄准；无需按住鼠标拖动视角。"),TEXT("按住左键蓄力，松开抛投。朝水面上方瞄准可增加抛投距离。"),TEXT("按住右键收线；空格抽饵。停顿与水层决定鱼是否追饵。"),TEXT("出现咬口提示时按空格刺鱼。搏鱼时避免张力进入红区。"),TEXT("滚轮调泄力：鱼发力时松开收线或降低泄力。"),TEXT("Tab 换拟饵；V 切换水下观察 / 鱼获近景；R 收竿或放流。"),TEXT("Esc 打开菜单。上鱼后自动记录鱼获和个人设置。")};
   for(int i=0;i<7;++i)Text(H[i],80,260+i*39,20,i%2?Muted:White);
   Button(TEXT("返回"),80,592,200,TEXT("back"));
  }return;
 }
 Rect(24,24,330,102,FLinearColor(.012f,.025f,.024f,.78f));Text(TEXT("野水  /  ")+P->SpotName(),42,36,24,White);Text(P->WeatherName()+TEXT(" · ")+P->TimeName(),42,74,16,Muted);Text(TEXT("Esc 菜单"),245,99,13,Muted);
 Rect(24,553,465,143,FLinearColor(.012f,.025f,.024f,.82f));Text(P->LureName(),42,565,21,Accent);Text(FString::Printf(TEXT("距离 %.1f m    水深 %.1f m    泄力 %.0f%%"),P->DistanceMetres(),P->Depth,P->Drag*100),42,599,16,White);
 Text(TEXT("左键 抛投  /  右键 收线  /  空格 抽饵与刺鱼"),42,636,15,Muted);Text(TEXT("Tab 换饵  ·  V 观察  ·  R 收竿/放流"),42,663,15,Muted);
 if(P->Phase==EFishingPhase::Ready)Text(P->Notice,410,484,18,White);
 if(P->Phase==EFishingPhase::Charging){Text(TEXT("抛投力度"),490,459,18,White);Rect(490,489,300,8,FLinearColor(.08f,.13f,.12f));Rect(490,489,P->Charge*300,8,Accent);}
 if(P->Phase==EFishingPhase::Bite){Rect(475,193,330,70,FLinearColor(.06f,.16f,.12f,.93f));Text(TEXT("咬口！ 按 空格 刺鱼"),507,214,25,FLinearColor(1,.77f,.35f));}
 if(P->Phase==EFishingPhase::Retrieving)Text(P->FishStatus(),490,484,18,White);
 if(P->Phase==EFishingPhase::Fighting){Text(TEXT("鱼线张力"),490,457,18,White);Rect(490,487,300,12,FLinearColor(.1f,.13f,.12f));Rect(580,487,165,12,FLinearColor(.09f,.32f,.22f));Rect(490,487,P->Tension*300,5,P->Tension>.85f?FLinearColor(1,.25f,.12f):Accent);Text(FString::Printf(TEXT("鱼的体力 %.0f%%  ·  滚轮调整泄力"),P->Stamina*100),490,510,16,Muted);}
 if(P->Phase==EFishingPhase::Landed){Rect(415,177,600,107,Panel);Text(TEXT("成功上鱼 · 已记入手册"),440,191,21,Accent);Text(P->LastCatch,440,225,26,White);Text(TEXT("V 近景查看    R 放流"),440,264,15,Muted);}
 if(!P->bObserve){Rect(638,356,4,8,FLinearColor(.8f,.9f,.8f,.65f));Rect(636,358,8,4,FLinearColor(.8f,.9f,.8f,.65f));}
}


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
 const bool bAssist=P->SaveData && P->SaveData->bFishingAssist;
 if(!ChineseFont){ChineseFont=NewObject<UFont>(this);ChineseFont->FontCacheType=EFontCacheType::Runtime;ChineseFont->LegacyFontSize=20;ChineseFont->GetMutableInternalCompositeFont().DefaultTypeface.Fonts.Add(FTypefaceEntry(TEXT("Regular"),FPaths::ProjectContentDir()/TEXT("UI/Chinese.ttf"),EFontHinting::Default,EFontLoadingPolicy::LazyLoad));}
 const float S=FMath::Min(Canvas->SizeX/1280.f,Canvas->SizeY/720.f);const float OX=(Canvas->SizeX-1280*S)/2,OY=(Canvas->SizeY-720*S)/2;
 const FLinearColor White(.93f,.96f,.91f),Muted(.61f,.72f,.68f),Accent(.35f,.8f,.67f),Amber(1.f,.72f,.3f),Danger(1.f,.32f,.23f),Panel(.012f,.025f,.024f,.9f);
 auto Rect=[&](float X,float Y,float W,float H,FLinearColor C){DrawRect(C,OX+X*S,OY+Y*S,W*S,H*S);};
 auto Text=[&](const FString& T,float X,float Y,float Size,FLinearColor C){FCanvasTextItem Item(FVector2D(OX+X*S,OY+Y*S),FText::FromString(T),FSlateFontInfo(ChineseFont,FMath::RoundToInt(Size*S*.75f)),C);Item.EnableShadow(FLinearColor(0,0,0,.65f),FVector2D(S,S));Canvas->DrawItem(Item);};
 auto Rule=[&](float X,float Y,float W){Rect(X,Y,W,1,FLinearColor(.21f,.35f,.30f,.65f));};
 auto Meter=[&](float X,float Y,float W,float Value,FLinearColor C){Rect(X,Y,W,6,FLinearColor(.10f,.17f,.15f));Rect(X,Y,W*FMath::Clamp(Value,0.f,1.f),6,C);};
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
   Text(TEXT("岸钓更新 2026.09.22  ·  本地自动保存"),80,624,15,Muted);
  }else if(P->MenuPage==1){
   Text(TEXT("环境与设置"),80,204,28,White);
   Button(TEXT("天气：")+P->WeatherName(),80,260,490,TEXT("weather"));Button(TEXT("时段：")+P->TimeName(),80,316,490,TEXT("time"));Button(TEXT("标点：")+P->SpotName()+TEXT("（切换时收竿）"),80,372,490,TEXT("spot"));
   Text(FString::Printf(TEXT("鼠标灵敏度  %.2f"),P->Sensitivity),680,267,20,White);Button(TEXT("－"),990,257,64,TEXT("sens-"));Button(TEXT("＋"),1066,257,64,TEXT("sens+"));
   Text(FString::Printf(TEXT("声音音量  %.0f%%"),P->Volume*100),680,327,20,White);Button(TEXT("－"),990,317,64,TEXT("volume-"));Button(TEXT("＋"),1066,317,64,TEXT("volume+"));
   const TCHAR* Quality[]={TEXT("性能"),TEXT("均衡"),TEXT("精细")};Button(FString(TEXT("画质："))+Quality[P->SaveData->Quality],680,377,450,TEXT("quality"));Button(P->SaveData->bFullscreen?TEXT("显示：无边框全屏"):TEXT("显示：窗口"),680,433,450,TEXT("fullscreen"));
   Button(bAssist?TEXT("钓鱼辅助：开启"):TEXT("钓鱼辅助：关闭"),80,433,490,TEXT("fishing-assist"));
   Text(bAssist?TEXT("已开启：V 水下观察、跟饵状态、刺鱼亮区与搏鱼提示。"):TEXT("岸钓：看水面和竿线，听泄力声；需要时可开启辅助。"),80,505,18,Muted);
   Text(TEXT("天气与时段会影响鱼的活跃度。笔记本建议使用“均衡”。"),80,541,17,Muted);Button(TEXT("返回"),80,592,200,TEXT("back"));
  }else if(P->MenuPage==2){
   Text(TEXT("鱼获手册"),80,202,28,White);Text(TEXT("最近 8 次上鱼 / 本地保留最近 100 条记录"),400,209,17,Muted);
   if(P->SaveData->Journal.IsEmpty())Text(TEXT("还没有鱼获。到沉木附近试一试抽停米诺。"),80,295,22,Muted);
   for(int i=0;i<FMath::Min(8,P->SaveData->Journal.Num());++i){auto& R=P->SaveData->Journal[i];float Y=262+i*36;Text(R.Species,80,Y,19,White);Text(FString::Printf(TEXT("%.2f kg  /  %.0f cm"),R.Weight,R.Length),325,Y,18,Accent);Text(R.Lure,610,Y,18,Muted);Text(R.Date,870,Y,17,Muted);}
   Button(TEXT("返回"),80,596,200,TEXT("back"));
  }else{
   Text(TEXT("操作指南"),80,202,28,White);
   const TCHAR* H[]={TEXT("W A S D 移动，鼠标瞄准；按住左键蓄力，松开抛投。"),TEXT("按住右键收线，空格抽饵；试着收、停、抽，观察水面与竿线。"),TEXT("线突然绷紧、竿尖顿下时，按空格刺鱼；听泄力声判断鱼是否在出线。"),TEXT("搏鱼时鼠标或 A / D 左右压竿；W / S 抬高或压低竿尖。"),TEXT("鱼线吃紧时松开右键，滚轮调松泄力；竿线放缓后再收线。"),TEXT("鱼到岸边后及时按空格抄鱼；R 放流，V 查看鱼获。"),TEXT("Tab 换拟饵；Esc 菜单。需要水下观察或提示时，在设置开启钓鱼辅助。")};
   for(int i=0;i<7;++i)Text(H[i],80,260+i*39,20,i%2?Muted:White);
   Button(TEXT("返回"),80,592,200,TEXT("back"));Button(TEXT("钓鱼辅助设置"),304,592,250,TEXT("settings"));
  }return;
 }
 Rect(24,24,310,88,FLinearColor(.012f,.025f,.024f,.78f));
 Text(TEXT("野水  /  ")+P->SpotName(),42,35,23,White);
 Text(P->WeatherName()+TEXT(" · ")+P->TimeName(),42,72,15,Muted);Text(TEXT("Esc 菜单"),255,43,12,Muted);

 // Phase prompts own the headline while the player must strike, net, or review a catch.
 const bool bOwnsHeadline=P->Phase==EFishingPhase::Bite||P->Phase==EFishingPhase::Landing||P->Phase==EFishingPhase::Landed;
 if(P->EventLife>0&&!P->EventTitle.IsEmpty()&&!bOwnsHeadline&&(bAssist||P->Phase!=EFishingPhase::Fighting)){
  const float Remaining=FMath::Clamp(P->EventLife/FMath::Max(.01f,P->EventDuration),0.f,1.f);
  const float Fade=FMath::Min(1.f,P->EventLife/.3f);
  FLinearColor EventColor=P->Phase==EFishingPhase::Fighting&&P->Fight.Move!=EFightMove::Recover?Amber:Accent;
  if(P->Fight.bBroken||P->Fight.bLost)EventColor=Danger;
  FLinearColor EventWhite=White;EventWhite.A=Fade;EventColor.A=Fade;
  Rect(452,30,514,88,FLinearColor(.012f,.025f,.024f,.83f*Fade));Rect(452,30,3,88,EventColor);
  Text(P->EventTitle,473,40,25,EventColor);Text(P->EventDetail,473,77,16,EventWhite);
  if(bAssist)Rect(473,109,470*Remaining,2,EventColor);
 }

 if(P->Phase!=EFishingPhase::Fighting&&P->Phase!=EFishingPhase::Landing&&P->Phase!=EFishingPhase::Landed&&P->Phase!=EFishingPhase::Releasing){
  Rect(24,561,465,135,FLinearColor(.012f,.025f,.024f,.84f));
  Text(P->LureName(),42,573,21,Accent);
  Text(bAssist?FString::Printf(TEXT("距离 %.1f m    水深 %.1f m    泄力 %.0f%%"),P->DistanceMetres(),P->Depth,P->Drag*100):FString::Printf(TEXT("滚轮调节泄力  %.0f%%  ·  留意竿尖与鱼线"),P->Drag*100),42,606,16,White);
  Text(TEXT("左键 抛投  /  右键 收线  /  空格 抽饵与刺鱼"),42,641,15,Muted);
  Text(bAssist?TEXT("Tab 换饵  ·  V 水下观察  ·  R 收竿"):TEXT("Tab 换饵  ·  R 收竿  ·  Esc 设置 / 辅助"),42,670,14,Muted);
 }
 if(P->Phase==EFishingPhase::Ready&&P->EventLife<=0)Text(P->Notice,42,521,17,White);
 if(P->Phase==EFishingPhase::Charging){
  Text(TEXT("松开左键，送出拟饵"),490,446,21,White);
  Meter(490,484,300,P->Charge,Accent);Text(FString::Printf(TEXT("抛投力度  %.0f%%"),P->Charge*100),490,501,15,Muted);
 }
 if(bAssist&&P->Phase==EFishingPhase::Retrieving){
  Text(P->FishStatus(),42,488,20,White);Text(P->CadenceHint(),42,526,16,Accent);
 }
 if(bAssist&&P->Phase==EFishingPhase::Bite){
  const float Progress=P->BiteProgress();
  const bool bSweetSpot=Progress>=.2f&&Progress<=.7f;
  const FLinearColor BiteColor=Progress>.7f?Danger:Amber;
  Rect(444,145,392,158,FLinearColor(.025f,.036f,.025f,.91f));Rect(444,145,3,158,BiteColor);
  Text(TEXT("咬口"),466,157,17,BiteColor);Text(TEXT("空格  刺鱼"),466,184,38,White);
  Text(bSweetSpot?TEXT("现在！亮区刺鱼，挂钩更稳"):Progress<.2f?TEXT("稳住，等标记进入亮区"):TEXT("即将吐饵，立刻刺鱼"),466,237,16,BiteColor);
  // The right edge shrinks leftwards; .2-.7 elapsed maps to .8-.3 remaining.
  const float X=466,Y=278,W=348,Marker=X+W*(1.f-Progress);
  Rect(X,Y,W,10,FLinearColor(.10f,.15f,.12f));Rect(X+W*.3f,Y,W*.5f,10,FLinearColor(.66f,.43f,.13f));
  Rect(X,Y+3,W*(1.f-Progress),4,BiteColor);Rect(Marker-1,Y-5,3,20,White);
 }
 if(bAssist&&P->Phase==EFishingPhase::Fighting){
  const FFishingFight& F=P->Fight;
  const bool bTelegraph=F.IsTelegraphing(),bSurge=F.IsSurging(),bRecover=F.Move==EFightMove::Recover;
  const FLinearColor MoveColor=bRecover?Accent:Amber;
  Rect(24,384,420,312,FLinearColor(.012f,.025f,.024f,.88f));Rect(24,384,3,312,MoveColor);
  Text(bTelegraph?TEXT("搏鱼  /  即将发力"):bRecover?TEXT("搏鱼  /  回气窗口"):bSurge?TEXT("搏鱼  /  正在冲击"):TEXT("搏鱼  /  正在挣脱"),42,398,14,MoveColor);
  Text(F.MoveName(),42,424,29,White);
  const float Side=F.RequiredSide();
  if(FMath::Abs(Side)>.1f){
   const float CX=377,CY=444,Dir=Side<0?-1.f:1.f;
   DrawLine(OX+(CX-Dir*18)*S,OY+CY*S,OX+(CX+Dir*18)*S,OY+CY*S,MoveColor,3*S);
   DrawLine(OX+(CX+Dir*18)*S,OY+CY*S,OX+(CX+Dir*7)*S,OY+(CY-10)*S,MoveColor,3*S);
   DrawLine(OX+(CX+Dir*18)*S,OY+CY*S,OX+(CX+Dir*7)*S,OY+(CY+10)*S,MoveColor,3*S);
   Text(Side<0?TEXT("A 左压"):TEXT("D 右压"),354,405,12,MoveColor);
  }
  Text(F.Instruction(),42,473,16,MoveColor);
  const float T=FMath::Clamp(F.Tension,0.f,1.f);
  const FLinearColor TensionColor=T>.88f?Danger:T>.75f||T<.28f?Amber:Accent;
  Text(T>.88f?TEXT("张力过高 · 松开右键"):T<.20f?TEXT("鱼线偏松 · 轻收线"):TEXT("鱼线张力"),42,505,15,TensionColor);
  Text(FString::Printf(TEXT("%.0f%%"),F.Tension*100),367,505,15,TensionColor);
  const float TX=42,TY=532,TW=384;
  Rect(TX,TY,TW,9,FLinearColor(.11f,.17f,.14f));Rect(TX+TW*.28f,TY,TW*.47f,9,FLinearColor(.075f,.31f,.23f));
  Rect(TX+TW*.75f,TY,TW*.13f,9,FLinearColor(.38f,.26f,.10f));Rect(TX+TW*.88f,TY,TW*.12f,9,FLinearColor(.41f,.10f,.065f));
  Rect(TX,TY+3,TW*T,3,TensionColor);Rect(TX+TW*T-1,TY-4,3,17,White);
  Text(FString::Printf(TEXT("鱼的体力  %.0f%%"),FMath::Clamp(F.Energy,0.f,1.f)*100),42,555,16,White);
  Text(FString::Printf(TEXT("距岸 %.1f m"),F.Distance),292,555,16,White);Meter(42,584,384,F.Energy,Accent);
  FString Warning;
  if(F.LineCondition<.55f)Warning=FString::Printf(TEXT("线况受损 %.0f%%"),FMath::Max(0.f,F.LineCondition)*100);
  if(F.HookSecurity<.55f){if(!Warning.IsEmpty())Warning+=TEXT("  ·  ");Warning+=TEXT("挂钩松动，避免松线");}
  if(!Warning.IsEmpty())Text(Warning,42,602,14,(F.LineCondition<.25f||F.HookSecurity<.25f)?Danger:Amber);
  else Text(TEXT("保持亮区张力，等它回气再争取距离"),42,602,14,Muted);
  Rule(42,630,384);
  Text(bRecover?TEXT("按住右键收线，抓住回气窗口"):bSurge?TEXT("松开右键卸力，按提示控制竿尖"):F.Move==EFightMove::Jump?TEXT("松开右键，压低竿尖应对洗鳃"):TEXT("保持侧向压竿，稳住鱼线张力"),42,639,16,MoveColor);
  Text(FString::Printf(TEXT("鼠标 / A D / W S 控竿  ·  滚轮泄力 %.0f%%"),P->Drag*100),42,671,14,Muted);
 }
 if(!bAssist&&P->Phase==EFishingPhase::Fighting){
  const FFishingFight& F=P->Fight;
  const bool bTooTight=F.Tension>.88f,bTooLoose=F.Tension<.20f;
  const FLinearColor SafetyColor=bTooTight?Danger:bTooLoose?Amber:Accent;
  Rect(24,536,465,160,FLinearColor(.012f,.025f,.024f,.86f));Rect(24,536,3,160,SafetyColor);
  Text(TEXT("稳住竿线"),42,549,23,White);
  Text(bTooTight?TEXT("鱼线吃紧 · 松开右键，调松泄力"):bTooLoose?TEXT("鱼线偏松 · 轻收线，保持接触"):TEXT("看竿尖和线的走向，听泄力声"),42,584,17,SafetyColor);
  if(F.LineCondition<.55f)Text(TEXT("鱼线已受损，避免继续硬拉"),42,612,14,F.LineCondition<.25f?Danger:Amber);
  else Text(TEXT("鱼往一侧拉时向另一侧压竿；出线时先卸力"),42,612,14,Muted);
  Text(TEXT("右键收线  ·  鼠标 / A D / W S 控竿"),42,640,15,White);
  Text(FString::Printf(TEXT("滚轮泄力 %.0f%%  ·  Esc 设置 / 辅助"),P->Drag*100),42,670,14,Muted);
 }
 if(P->Phase==EFishingPhase::Landing){
  const float Progress=P->LandingProgress(),Seconds=4.f*(1.f-Progress);
  const FLinearColor NetColor=bAssist&&Seconds<1.f?Danger:Amber;
  Rect(438,152,404,bAssist?160:140,FLinearColor(.012f,.025f,.024f,.91f));Rect(438,152,3,bAssist?160:140,NetColor);
  Text(TEXT("鱼已到岸边  /  抓住最后一步"),460,166,16,NetColor);
  Text(TEXT("空格  抄鱼入网"),460,196,34,White);
  Text(bAssist?FString::Printf(TEXT("抄网窗口  %.1f 秒"),Seconds):TEXT("趁鱼靠岸，及时入网"),460,252,18,NetColor);
  if(bAssist)Meter(460,292,360,1.f-Progress,NetColor);
 }
 if(P->Phase==EFishingPhase::Landed){
  Rect(24,157,444,259,FLinearColor(.012f,.025f,.024f,.93f));Rect(24,157,4,259,Accent);
  Text(TEXT("鱼获已入册"),46,174,15,Accent);Text(TEXT("成功上鱼"),46,201,37,White);
  Text(P->CatchGrade,312,213,22,Amber);Text(P->LastCatch,46,258,23,White);Rule(46,299,398);
  Text(FString::Printf(TEXT("%d 分  ·  +%d 经验"),P->CatchScore,P->CatchXP),46,312,20,Accent);
  FString Milestone;
  if(P->bPersonalBest)Milestone=TEXT("个人纪录刷新");
  if(P->bNewSpecies){if(!Milestone.IsEmpty())Milestone+=TEXT("  ·  ");Milestone+=TEXT("首次发现此鱼种");}
  if(!Milestone.IsEmpty())Text(Milestone,46,346,16,Amber);
  Text(TEXT("R 放流    ·    V 鱼获近景"),46,382,18,White);
 }
 if(P->Phase==EFishingPhase::Releasing){
  Rect(410,600,460,70,FLinearColor(.012f,.025f,.024f,.85f));
  Text(TEXT("轻放回水中，让它游走…"),441,622,23,Accent);
 }
 if(!P->bObserve&&P->Phase!=EFishingPhase::Landed&&P->Phase!=EFishingPhase::Releasing){Rect(638,356,4,8,FLinearColor(.8f,.9f,.8f,.65f));Rect(636,358,8,4,FLinearColor(.8f,.9f,.8f,.65f));}
}


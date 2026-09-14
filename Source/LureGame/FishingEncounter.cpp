#include "FishingEncounter.h"

void FFishingFight::Start(float Weight,int32 Species,float Quality,float Metres){
 *this=FFishingFight();Strength=FMath::Clamp(.72f+FMath::Sqrt(FMath::Max(.1f,Weight))*.3f,.8f,1.5f);
 Seed=Species*37+FMath::RoundToInt(Weight*100);Distance=FMath::Max(6.f,Metres);
 HookSecurity=FMath::Lerp(.50f,.97f,FMath::Clamp(Quality,0.f,1.f));
 MoveIndex=-1;AdvanceMove();
}
void FFishingFight::AdvanceMove(){
 ++MoveIndex;MoveTime=0;
 if(MoveIndex%2){Move=EFightMove::Recover;MoveDuration=3.6f;return;}
 int32 Choice=(Seed+MoveIndex/2*3)%5;
 const EFightMove Moves[]={EFightMove::RunLeft,EFightMove::RunRight,EFightMove::Dive,EFightMove::HeadShake,EFightMove::Jump};
 // A first run establishes the opponent immediately, with a readable wind-up.
 Move=MoveIndex==0?(Seed%2?EFightMove::RunRight:EFightMove::RunLeft):Moves[Choice];
 MoveDuration=Move==EFightMove::Jump?2.0f:(Move==EFightMove::HeadShake?2.6f:3.3f);
}
bool FFishingFight::IsSurging() const{return Move==EFightMove::RunLeft||Move==EFightMove::RunRight||Move==EFightMove::Dive;}
bool FFishingFight::IsTelegraphing() const{return Move!=EFightMove::Recover&&MoveTime<.75f;}
float FFishingFight::RequiredSide() const{return Move==EFightMove::RunLeft?1.f:(Move==EFightMove::RunRight?-1.f:0.f);}
void FFishingFight::Step(float Dt,const FFightInput& In){
 if(bBroken||bLost)return;
 Dt=FMath::Clamp(Dt,0.f,.1f);Time+=Dt;MoveTime+=Dt;
 if(MoveTime>MoveDuration)AdvanceMove();
 float Drag=FMath::Clamp(In.Drag,.1f,1.f),Side=FMath::Clamp(In.RodSide,-1.f,1.f),Lift=FMath::Clamp(In.RodLift,-1.f,1.f);
 const float Windup=FMath::Clamp((MoveTime-.75f)/.4f,0.f,1.f);
 bool Counter=RequiredSide()!=0 && Side*RequiredSide()>.3f;
 bool Wrong=RequiredSide()!=0 && Side*RequiredSide()<-.3f;
 bool Posture=Move==EFightMove::Dive?Lift>.2f:(Move==EFightMove::Jump?Lift<-.2f:true);
 if(Move==EFightMove::Recover)Pull=.23f;
 else if(IsSurging())Pull=FMath::Lerp(.4f,1.48f,Windup);
 else if(Move==EFightMove::HeadShake)Pull=.52f+Windup*(.22f+.26f*FMath::Sin(MoveTime*17));
 else Pull=FMath::Lerp(.45f,.18f,Windup);
 Pull*=FMath::Lerp(.55f,1.f,Energy)*Strength;
 float Target=.12f+Drag*.58f+Pull*.35f+(In.bReeling?.18f:0.f);
 Target+=Wrong?.13f:0.f;Target-=Counter?.14f:0.f;
 if(Move==EFightMove::Jump)Target+=Lift>.2f?.20f:(Posture?.03f:.09f);
 if(Move==EFightMove::Dive&&!Posture)Target+=.10f;
 // Steady lateral pressure keeps a small bend when a fish swims toward you.
 if(Move==EFightMove::HeadShake && FMath::Abs(Side)>.25f)Target+=.05f;
 Tension=FMath::FInterpTo(Tension,FMath::Clamp(Target,.03f,1.35f),Dt,4.5f);
 if(Tension>1.f)LineCondition-=Dt*(Tension-1.f)*2.8f;
 if(Tension<.20f)HookSecurity-=Dt*(.20f-Tension)*1.8f;
 if(Move==EFightMove::HeadShake && (Tension<.3f||Tension>1.02f))HookSecurity-=Dt*.12f;
 if(Move==EFightMove::Jump&&!Posture&&Windup>.1f)HookSecurity-=Dt*.10f;
 LineCondition=FMath::Clamp(LineCondition,0.f,1.f);HookSecurity=FMath::Clamp(HookSecurity,0.f,1.f);
 Control=(Tension>.28f&&Tension<.9f)?1.f:0.f;
 if(IsSurging()&&Windup>.1f)Control*=(!In.bReeling&&(Counter||Move==EFightMove::Dive)&&Posture)?1.f:.35f;
 if(Move==EFightMove::Jump)Control*=Posture?1.f:0.f;
 CleanSeconds+=Control*Dt;
 const float Work=(.013f+.022f*Control)/Strength;
 Energy=FMath::Clamp(Energy-Dt*Work+(Tension<.2f?Dt*.012f:0.f),0.f,1.f);
 float Outward=IsSurging()?Windup*(.9f+Energy*1.8f)*(1-Drag)*Strength*(Counter?.55f:1.f):0.f;
 float Inward=In.bReeling?(Move==EFightMove::Recover?2.8f:1.0f)*(1-Energy*.4f)*FMath::Clamp(Drag*1.7f,.15f,1.f):0.f;
 Distance=FMath::Max(1.5f,Distance+(Outward-Inward)*Dt);
 if(Move==EFightMove::RunLeft||Move==EFightMove::RunRight)LateralOffset+=-RequiredSide()*Windup*Dt*(Counter?.6f:1.5f);
 LateralOffset=FMath::Clamp(LateralOffset,-9.f,9.f);
 JumpHeight=Move==EFightMove::Jump?FMath::Max(0.f,FMath::Sin(FMath::Clamp((MoveTime-.75f)/1.1f,0.f,1.f)*PI))*1.15f:0.f;
 bBroken=LineCondition<=0;bLost=HookSecurity<=0||Distance>95;
}
FString FFishingFight::MoveName() const{
 switch(Move){
 case EFightMove::Recover:return TEXT("它在喘息 · 收线机会");
 case EFightMove::RunLeft:return IsTelegraphing()?TEXT("鱼头转向左侧…"):TEXT("向左急冲！");
 case EFightMove::RunRight:return IsTelegraphing()?TEXT("鱼头转向右侧…"):TEXT("向右急冲！");
 case EFightMove::Dive:return IsTelegraphing()?TEXT("它要往深处钻…"):TEXT("鱼正在下潜！");
 case EFightMove::HeadShake:return TEXT("猛烈甩头");
 default:return IsTelegraphing()?TEXT("它正在冲向水面…"):TEXT("洗鳃！");
 }
}
FString FFishingFight::Instruction() const{
 if(Tension>1.f)return TEXT("线快撑不住了！松开右键，滚轮向下减泄力");
 if(HookSecurity<.25f)return TEXT("钩口不稳 · 保持适度张力，别让鱼线松掉");
 switch(Move){
 case EFightMove::Recover:return TEXT("按住右键回收距离 · 留意下一次发力");
 case EFightMove::RunLeft:return TEXT("松开收线 · 向右压竿（鼠标 / D）");
 case EFightMove::RunRight:return TEXT("松开收线 · 向左压竿（鼠标 / A）");
 case EFightMove::Dive:return TEXT("停止硬收 · 抬高竿尖（鼠标 / W）");
 case EFightMove::HeadShake:return TEXT("保持竿弯 · 侧向稳住，别给松线");
 default:return TEXT("压低竿尖（鼠标 / S）· 暂停收线");
 }
}

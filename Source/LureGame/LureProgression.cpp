#include "LureWorld.h"
#include "LureSave.h"
#include "Kismet/GameplayStatics.h"
#include "HAL/PlatformMisc.h"

namespace {
constexpr int32 AllMilestones=63;
const TCHAR* SpeciesNames[]={TEXT("大口黑鲈"),TEXT("河鲈"),TEXT("白斑狗鱼"),TEXT("虹鳟")};
const TCHAR* MilestoneNames[]={TEXT("第一尾鱼"),TEXT("把握咬口"),TEXT("从容控鱼"),TEXT("读懂湖湾"),TEXT("四种相遇"),TEXT("奖杯时刻")};
const int32 Bonuses[]={50,100,150,250,300,350};
const int32 RankXP[]={0,400,1000,2200,4500};
const TCHAR* Ranks[]={TEXT("初探者"),TEXT("识水者"),TEXT("追猎者"),TEXT("熟练钓手"),TEXT("湖湾大师")};
int32 SpeciesIndex(const FString& Name){for(int32 I=0;I<4;++I)if(Name==SpeciesNames[I])return I;return INDEX_NONE;}
int32 BitCount(int32 Mask){int32 Count=0;for(int32 I=0;I<3;++I)Count+=(Mask>>I)&1;return Count;}
int32 SpeciesCount(const ULureSave* Save){
 if(!Save)return 0;
 int32 Mask=0;
 for(const auto& Best:Save->SpeciesBests){int32 I=SpeciesIndex(Best.Key);if(I!=INDEX_NONE && Best.Value>0)Mask|=1<<I;}
 for(const FCatchRecord& R:Save->Journal){int32 I=SpeciesIndex(R.Species);if(I!=INDEX_NONE && R.Weight>0)Mask|=1<<I;}
 int32 Count=0;for(int32 I=0;I<4;++I)Count+=(Mask>>I)&1;return Count;
}
int32 NextMilestone(const ULureSave* Save){for(int32 I=0;I<6;++I)if(!Save || !(Save->CompletedMilestones&(1<<I)))return I;return INDEX_NONE;}
int32 RankIndex(int32 XP){int32 I=0;while(I<4 && XP>=RankXP[I+1])++I;return I;}
}

float ALurePawn::TrophyThreshold(int32 Species){const float Kg[]={2.7f,.8f,5.5f,2.1f};return Species>=0 && Species<4?Kg[Species]:MAX_flt;}
FString ALurePawn::RankName() const {return Ranks[RankIndex(SaveData?SaveData->Experience:0)];}
float ALurePawn::RankProgress() const {
 const int32 XP=SaveData?SaveData->Experience:0,I=RankIndex(XP);
 return I==4?1.f:FMath::Clamp(float(XP-RankXP[I])/float(RankXP[I+1]-RankXP[I]),0.f,1.f);
}
FString ALurePawn::ProgressTitle() const {
 const int32 I=NextMilestone(SaveData);
 return I==INDEX_NONE?TEXT("下一尾，刷新纪录"):FString::Printf(TEXT("湖湾目标 · %s"),MilestoneNames[I]);
}
FString ALurePawn::ProgressDetail() const {
 switch(NextMilestone(SaveData)){
 case 0:return TEXT("钓获并抄起第一尾鱼 · 奖励 50 XP");
 case 1:return TEXT("咬口进度接近中间时刺鱼，时机达到 85% · 奖励 100 XP");
 case 2:return TEXT("搏鱼至少 8 秒，控鱼率 ≥80%、剩余线况 ≥90% · 奖励 150 XP");
 case 3:{
  const int32 Mask=SaveData?SaveData->CaughtSpots:0;
  const TCHAR* Spots[]={TEXT("沉木湾"),TEXT("芦苇浅滩"),TEXT("岩石岬角")};FString Missing;
  for(int32 I=0;I<3;++I)if(!(Mask&(1<<I))){if(!Missing.IsEmpty())Missing+=TEXT("、");Missing+=Spots[I];}
  return FString::Printf(TEXT("标点鱼获 %d/3 · 待完成：%s · 奖励 250 XP"),BitCount(Mask),*Missing);
 }
 case 4:return FString::Printf(TEXT("鱼种 %d/4 · 黑鲈、河鲈、狗鱼、虹鳟 · 奖励 300 XP"),SpeciesCount(SaveData));
 case 5:return TEXT("奖杯鱼：黑鲈 2.7 / 河鲈 0.8 / 狗鱼 5.5 / 虹鳟 2.1 kg · 奖励 350 XP");
 default:return FString::Printf(TEXT("六项目标已完成 · 累计奖杯 %d 尾 · 继续挑战各鱼种个人纪录"),SaveData?SaveData->TrophyCatches:0);
 }
}
float ALurePawn::ProgressFraction() const {
 if(!SaveData)return 0;
 switch(NextMilestone(SaveData)){
 case 0:return 0;
 case 1:return SaveData->Journal.IsEmpty()?0:FMath::Clamp(SaveData->Journal[0].HookQuality/.85f,0.f,1.f);
 case 2:return Fight.Time>0?FMath::Clamp(FMath::Min3(Fight.CleanSeconds/Fight.Time/.8f,Fight.LineCondition/.9f,Fight.Time/8.f),0.f,1.f):0;
 case 3:return BitCount(SaveData->CaughtSpots)/3.f;
 case 4:return SpeciesCount(SaveData)/4.f;
 case 5:{float Best=0;for(int32 I=0;I<4;++I)Best=FMath::Max(Best,SaveData->SpeciesBests.FindRef(SpeciesNames[I])/TrophyThreshold(I));return FMath::Clamp(Best,0.f,1.f);}
 default:return 1;
 }
}
void ALurePawn::UpdateProgression(){
 MilestoneXP=0;MilestoneText.Empty();bTrophy=false;
 if(!SaveData || SaveData->Journal.IsEmpty())return;
 FCatchRecord& Latest=SaveData->Journal[0];
 if(Latest.SpotId>=0 && Latest.SpotId<3)SaveData->CaughtSpots|=1<<Latest.SpotId;
 const int32 Species=SpeciesIndex(Latest.Species);
 bTrophy=Species!=INDEX_NONE && Latest.Weight>=TrophyThreshold(Species);
 if(bTrophy && !Latest.bTrophy)++SaveData->TrophyCatches;
 Latest.bTrophy=bTrophy;
 const float Control=Fight.Time>0?FMath::Clamp(Fight.CleanSeconds/Fight.Time,0.f,1.f):0;
 const bool Met[]={
  SaveData->TotalCatches>0 || Latest.Weight>0,
  Latest.HookQuality>=.85f,
  Latest.FightSeconds>=8.f && Control>=.8f && Fight.LineCondition>=.9f,
  (SaveData->CaughtSpots&7)==7,
  SpeciesCount(SaveData)==4,
  bTrophy
 };
 for(int32 I=0;I<6;++I)if(Met[I] && !(SaveData->CompletedMilestones&(1<<I))){
  SaveData->CompletedMilestones|=1<<I;MilestoneXP+=Bonuses[I];
  if(!MilestoneText.IsEmpty())MilestoneText+=TEXT(" · ");MilestoneText+=MilestoneNames[I];
 }
 CatchXP+=MilestoneXP;SaveData->Experience+=MilestoneXP;
 if(MilestoneXP)UE_LOG(LogTemp,Display,TEXT("LURE_PROGRESSION AWARD %s bonus=%d completed=%d"),*MilestoneText,MilestoneXP,SaveData->CompletedMilestones);
}

void ALurePawn::RunProgressionTest(){
 int32 Errors=0;auto Check=[&](bool Pass,const TCHAR* Name){UE_LOG(LogTemp,Display,TEXT("LURE_PROGRESSION %s: %s"),Pass?TEXT("PASS"):TEXT("FAIL"),Name);Errors+=!Pass;};
 SaveData=NewObject<ULureSave>(this);CatchXP=0;
 auto Catch=[&](int32 Species,float Weight,int32 AtSpot,float Hook,float Clean,float Seconds,float Line){
  FCatchRecord R;R.Species=SpeciesNames[Species];R.Weight=Weight;R.SpotId=AtSpot;R.HookQuality=Hook;R.FightSeconds=Seconds;
  SaveData->Journal.Insert(R,0);++SaveData->TotalCatches;float& Best=SaveData->SpeciesBests.FindOrAdd(R.Species);Best=FMath::Max(Best,Weight);
  Fight.Time=Seconds;Fight.CleanSeconds=Seconds*Clean;Fight.LineCondition=Line;CatchXP=0;UpdateProgression();
 };
 Catch(0,1,0,.3f,.4f,20,.95f);
 Check(MilestoneXP==50 && SaveData->CompletedMilestones==1,TEXT("first catch awards only earned objective"));
 const int32 FirstXP=SaveData->Experience;UpdateProgression();
 Check(MilestoneXP==0 && SaveData->Experience==FirstXP && CatchXP==50,TEXT("repeat evaluation cannot farm goal experience"));
 Catch(0,1.4f,0,.9f,.9f,7,.98f);
 Check(MilestoneXP==100 && SaveData->CompletedMilestones==3,TEXT("perfect hook awards once; short fight does not count as clean control"));
 Catch(0,1.4f,0,.9f,.9f,20,.89f);
 Check(MilestoneXP==0 && !(SaveData->CompletedMilestones&4),TEXT("damaged line prevents clean control milestone"));
 Catch(0,1.4f,0,.9f,.9f,20,.98f);
 Check(MilestoneXP==150 && (SaveData->CompletedMilestones&4),TEXT("sustained clean control earns objective"));
 Catch(1,.5f,1,.3f,.4f,20,.95f);Catch(2,2,2,.3f,.4f,20,.95f);
 Check(MilestoneXP==250 && SaveData->CaughtSpots==7 && SpeciesCount(SaveData)==3,TEXT("three actual catch locations complete lake objective"));
 Catch(3,1,2,.3f,.4f,20,.95f);
 Check(MilestoneXP==300 && (SaveData->CompletedMilestones&16),TEXT("four distinct species complete discovery objective"));
 Catch(0,2.7f,0,.3f,.4f,20,.95f);
 Check(bTrophy && MilestoneXP==350 && SaveData->CompletedMilestones==AllMilestones && SaveData->Experience==1200,TEXT("trophy boundary completes all six goals with exact one-time bonus total"));
 UpdateProgression();
 Check(MilestoneXP==0 && SaveData->TrophyCatches==1,TEXT("same trophy cannot be counted twice"));
 Catch(0,3,0,.3f,.4f,20,.95f);
 Check(MilestoneXP==0 && SaveData->TrophyCatches==2,TEXT("new trophy increments collection without repeating milestone reward"));
 const FString Slot=TEXT("Wildwater_ProgressionTest_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);
 bool Written=UGameplayStatics::SaveGameToSlot(SaveData,Slot,0);auto* Read=Cast<ULureSave>(UGameplayStatics::LoadGameFromSlot(Slot,0));
 Check(Written && Read && Read->CompletedMilestones==63 && Read->CaughtSpots==7 && Read->TrophyCatches==2 && Read->Experience==1200 && Read->Journal[0].bTrophy && Read->Journal[0].SpotId==0,TEXT("goals, trophies, catch location and XP survive isolated save reload"));
 if(Read){SaveData=Read;UpdateProgression();Check(MilestoneXP==0 && SaveData->Experience==1200 && SaveData->TrophyCatches==2,TEXT("reloaded trophy and goals remain idempotent"));}
 UGameplayStatics::DeleteGameInSlot(Slot,0);
 for(int32 I=0;I<4;++I){
  Catch(I,TrophyThreshold(I)-.001f,0,.3f,.4f,20,.95f);Check(!bTrophy,TEXT("fish below species trophy threshold is not a trophy"));
  Catch(I,TrophyThreshold(I),0,.3f,.4f,20,.95f);Check(bTrophy,TEXT("fish at species trophy threshold qualifies"));
 }
 for(int32 I=0;I<5;++I){SaveData->Experience=RankXP[I];Check(RankName()==Ranks[I] && FMath::IsNearlyEqual(RankProgress(),I==4?1.f:0.f),TEXT("rank threshold and progress boundary"));}
 SaveData=NewObject<ULureSave>(this);FCatchRecord Legacy;Legacy.Species=SpeciesNames[0];Legacy.Weight=1;SaveData->Journal.Add(Legacy);Fight=FFishingFight();
 UpdateProgression();Check(SaveData->CaughtSpots==0 && SaveData->CompletedMilestones==1,TEXT("legacy journal does not invent spot or skill achievements"));
 UE_LOG(LogTemp,Display,TEXT("LURE_PROGRESSION COMPLETE failures=%d"),Errors);FPlatformMisc::RequestExitWithStatus(false,Errors?1:0);
}

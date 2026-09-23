#include "LureWorld.h"
#include "FishingVisuals.h"
#include "CoveTerrain.h"
#include "Engine/World.h"
#include "HAL/PlatformMisc.h"
#include "HAL/PlatformTime.h"
#include "Misc/CommandLine.h"
#include "Misc/Parse.h"

namespace {
constexpr int32 HabitatCount=3;
constexpr int32 ResidentsPerHabitat=6;
constexpr int32 MaximumPerHabitat=8;
constexpr int32 ReplaySeed=731947;

bool UsesLegacyPopulation(){
 // These fixtures contain indexed fish references and calibrated cast paths.
 // Keep their five homes, offsets and response ranges exactly reproducible.
 const TCHAR* Flags[]={TEXT("LureSmokeTest"),TEXT("LureInputTest"),TEXT("LureSessionTest"),
  TEXT("LureEncounterTest"),TEXT("LureProgressionTest"),TEXT("LureCapture"),
  TEXT("LureMenuCapture"),TEXT("LureRigReview"),TEXT("LureEncounterCapture")};
 for(const TCHAR* Flag:Flags)if(FParse::Param(FCommandLine::Get(),Flag))return true;
 return false;
}

struct FResident {
 FVector Home;
 float Offset=0,NoticeRadius=0,TerritoryRadius=0;
 int32 Species=0,Habitat=0;
};

FVector SafeHabitatPosition(FVector Position){
 Position.X=FMath::Max(Position.X,static_cast<double>(Cove::ShoreX(Position.Y)+450.f));
 // Clearance includes the patrol's small vertical oscillation and body depth.
 Position.Z=FMath::Clamp(Position.Z,static_cast<double>(Cove::Height(Position.X,Position.Y)+65.f),-45.0);
 return Position;
}

TArray<FResident> MakeResidents(int32 Seed){
 FRandomStream Random(Seed);
 // Three distinct patches corresponding to the selectable shore positions:
 // timber/rock cover in the bay, the southern shallows, and the northern point.
 const FVector Homes[HabitatCount][ResidentsPerHabitat]={
  {FVector(1100,-150,-70),FVector(1500,450,-100),FVector(2050,800,-140),
   FVector(2400,250,-165),FVector(2850,-400,-200),FVector(3400,600,-235)},
  {FVector(950,-1700,-55),FVector(1450,-2100,-80),FVector(1800,-1400,-110),
   FVector(2100,-2350,-135),FVector(2650,-1850,-160),FVector(3150,-2550,-180)},
  {FVector(1200,1650,-100),FVector(1700,2150,-140),FVector(2100,1550,-180),
   FVector(2500,2450,-220),FVector(3050,1750,-260),FVector(3600,2350,-300)}
 };
 const int32 Species[HabitatCount][ResidentsPerHabitat]={{0,1,0,2,1,0},{1,0,1,2,0,1},{3,1,3,2,0,3}};
 TArray<FResident> Residents;
 for(int32 Habitat=0;Habitat<HabitatCount;++Habitat){
  for(int32 Slot=0;Slot<ResidentsPerHabitat;++Slot){
   FResident Resident;
   Resident.Habitat=Habitat;Resident.Species=Species[Habitat][Slot];
   // Separate draws keep replay order independent of function-argument
   // evaluation order across toolchains.
   const double JitterX=Random.FRandRange(-130.f,130.f);
   const double JitterY=Random.FRandRange(-120.f,120.f);
   const double JitterZ=Random.FRandRange(-18.f,18.f);
   Resident.Home=SafeHabitatPosition(Homes[Habitat][Slot]+FVector(JitterX,JitterY,JitterZ));
   Resident.Offset=Random.FRandRange(0.f,1000.f);
   Resident.NoticeRadius=Random.FRandRange(800.f,1000.f);
   Resident.TerritoryRadius=Random.FRandRange(1200.f,1450.f);
   Residents.Add(Resident);
  }
 }
 return Residents;
}

ALureFish* SpawnResident(UWorld* World,const FResident& Resident){
 ALureFish* Fish=World->SpawnActor<ALureFish>();
 if(!Fish)return nullptr;
 Fish->Initialize(Resident.Home,Resident.Offset);
 Fish->SetSpecies(Resident.Species);
 Fish->ConfigureHabitat(Resident.Habitat,Resident.NoticeRadius,Resident.TerritoryRadius);
 return Fish;
}
}

void ALurePawn::PopulateLake(){
 // Safe to call again: population setup never duplicates live actors.
 if(Fish.Num()>0)return;
 const bool bModernFixture=FParse::Param(FCommandLine::Get(),TEXT("LurePopulationTest")) ||
  FParse::Param(FCommandLine::Get(),TEXT("LureShoreCapture"));
 const bool bLegacy=!bModernFixture && UsesLegacyPopulation();
 const bool bDeterministic=bLegacy || bModernFixture;
 PopulationSeed=bDeterministic?ReplaySeed:static_cast<int32>(FPlatformTime::Cycles64()&0x7fffffff);
 PopulationGeneration=0;
 if(bLegacy){
  const FVector Homes[]={FVector(900,200,-65),FVector(1850,800,-95),FVector(2900,-500,-140),FVector(4100,1000,-100),FVector(5400,0,-120)};
  for(int32 Index=0;Index<UE_ARRAY_COUNT(Homes);++Index){
   if(ALureFish* Resident=GetWorld()->SpawnActor<ALureFish>()){
    Resident->Initialize(Homes[Index],Index*2.7f);Resident->SetSpecies(Index%4);Fish.Add(Resident);
   }
  }
 }else{
  for(const FResident& Resident:MakeResidents(PopulationSeed)){
   if(ALureFish* Spawned=SpawnResident(GetWorld(),Resident))Fish.Add(Spawned);
  }
 }
 UE_LOG(LogTemp,Display,TEXT("LURE_POPULATION seed=%d fish=%d legacy_fixture=%s"),PopulationSeed,Fish.Num(),bLegacy?TEXT("true"):TEXT("false"));
}

void ALurePawn::ReplenishFish(ALureFish* Released){
 if(!IsValid(Released) || Released->HabitatIndex<0 || Released->HabitatIndex>=HabitatCount ||
  Released->EncounterCount<=Released->LastPopulationEncounter)return;
 // One opportunity per actual release/escape, even if reset is called twice.
 Released->LastPopulationEncounter=Released->EncounterCount;
 ++PopulationGeneration;
 if(bObserve)return;
 const int32 Habitat=Released->HabitatIndex;
 int32 Count=0;
 for(ALureFish* Resident:Fish)if(IsValid(Resident) && Resident->HabitatIndex==Habitat)++Count;
 if(Count>=MaximumPerHabitat)return;
 const uint32 Seed=static_cast<uint32>(PopulationSeed)+static_cast<uint32>(PopulationGeneration)*196613u;
 FRandomStream Random(static_cast<int32>(Seed&0x7fffffffu));
 if(Random.FRand()>.55f)return;
 const TArray<FResident> Residents=MakeResidents(static_cast<int32>(Seed&0x7fffffffu));
 FResident Incoming=Residents[Habitat*ResidentsPerHabitat+Random.RandRange(3,ResidentsPerHabitat-1)];
 // Newcomers enter along the deeper outer edge, away from the current lure.
 const float HabitatY[]={200.f,-2050.f,1950.f};
 const double IncomingX=Random.FRandRange(3650.f,4250.f);
 const double IncomingY=HabitatY[Habitat]+Random.FRandRange(-450.f,450.f);
 const double IncomingZ=Random.FRandRange(-320.f,-235.f);
 Incoming.Home=SafeHabitatPosition(FVector(IncomingX,IncomingY,IncomingZ));
 const FVector Entry=SafeHabitatPosition(Incoming.Home+FVector(500.f,Random.FRandRange(-220.f,220.f),-30.f));
 if(FVector::DistSquared(Entry,LurePosition)<FMath::Square(1500.f) ||
  FVector::DistSquared(Entry,GetActorLocation())<FMath::Square(2200.f))return;
 if(ALureFish* Spawned=SpawnResident(GetWorld(),Incoming)){
  Spawned->SetActorLocation(Entry);
  Spawned->Cooldown=Random.FRandRange(9.f,15.f);
  Spawned->Behavior=EFishBehavior::Escaping;
  Fish.Add(Spawned);
  UE_LOG(LogTemp,Display,TEXT("LURE_POPULATION incoming habitat=%d generation=%d fish=%d"),Habitat,PopulationGeneration,Fish.Num());
 }
}

void ALurePawn::RunPopulationTest(){
 int32 Errors=0;
 auto Check=[&](bool bPass,const TCHAR* Label){
  UE_LOG(LogTemp,Display,TEXT("LURE_POPULATION_TEST %s: %s"),bPass?TEXT("PASS"):TEXT("FAIL"),Label);
  if(!bPass)++Errors;
 };
 const TArray<FResident> First=MakeResidents(ReplaySeed),Replay=MakeResidents(ReplaySeed),Other=MakeResidents(ReplaySeed+1);
 bool bReplayMatches=true,bDifferentSeed=false,bLayoutValid=true;
 int32 Counts[HabitatCount]={0,0,0};
 for(int32 Index=0;Index<First.Num();++Index){
  const FResident& Resident=First[Index];++Counts[Resident.Habitat];
  bReplayMatches&=Resident.Home==Replay[Index].Home && Resident.Offset==Replay[Index].Offset && Resident.Species==Replay[Index].Species;
  bDifferentSeed|=Resident.Home!=Other[Index].Home;
  bLayoutValid&=Resident.Home.Z<-40.f && Resident.Home.Z>Cove::Height(Resident.Home.X,Resident.Home.Y)+40.f;
  bLayoutValid&=(Resident.Habitat==0?FMath::Abs(Resident.Home.Y)<1000.f:
   (Resident.Habitat==1?Resident.Home.Y<-1200.f:Resident.Home.Y>1400.f));
 }
 Check(First.Num()==18 && Counts[0]==6 && Counts[1]==6 && Counts[2]==6 && bLayoutValid,TEXT("three populated habitat patches stay inside water and above the bottom"));
 Check(bReplayMatches && bDifferentSeed,TEXT("same seed reproduces layout; different seed changes residents"));
 const int32 OriginalCount=Fish.Num();PopulateLake();
 Check(OriginalCount==18 && Fish.Num()==OriginalCount,TEXT("population setup is idempotent"));

 ALureFish* Probe=SpawnResident(GetWorld(),First[0]);
 Check(Probe!=nullptr,TEXT("population behavior probe spawned"));
 if(Probe){
  const FVector Home=Probe->Home;const float Weight=Probe->Weight;
  FLurePresentation Presentation;Presentation.LureType=0;Presentation.RetrieveSpeed=180.f;
  Check(!Probe->CanRespondToLure(Home+FVector(0,0,300)) && !Probe->CanRespondToLure(Home+FVector(1600,0,0)),TEXT("wrong depth and distant presentations cannot draw a resident"));
  Probe->SetHooked(Home,0);Probe->Escape(true);
  const float ReleaseRest=Probe->Cooldown;
  bool bRestBite=false,bRestFollow=false;
  for(int32 Frame=0;Frame<1200;++Frame){
   Presentation.TwitchAge=FMath::Fmod(Frame/60.f,1.2f);
   bRestBite|=Probe->Simulate(1.f/60.f,Home,true,Presentation);
   bRestFollow|=Probe->Behavior==EFishBehavior::Following || Probe->Behavior==EFishBehavior::Attacking;
  }
  Check(ReleaseRest>=55.f && Probe->Cooldown>0 && !bRestBite && !bRestFollow && Probe->Wariness>0,
   TEXT("released fish ignores repeated close presentations through its rest period"));
  Check(Probe->Home==Home && Probe->Weight==Weight,TEXT("release preserves resident identity and habitat"));
  for(int32 Frame=0;Frame<12000;++Frame)Probe->Simulate(1.f/60.f,Home,false,Presentation);
  Check(Probe->Cooldown==0 && Probe->Wariness==0 && Probe->CanRespondToLure(Home),TEXT("rest and caution recover without forcing a bite"));
  Probe->Escape(false);
  Check(Probe->Cooldown>=22.f && Probe->Cooldown<ReleaseRest && !Probe->CanRespondToLure(Home),TEXT("escaped fish also rests before another encounter"));
  Probe->Destroy();
 }

 if(Fish.Num()>=18){
  LurePosition=FVector(150,0,-30);bObserve=false;
  ALureFish* Resident=Fish[0];Resident->Escape(true);ReplenishFish(Resident);
  const int32 Generation=PopulationGeneration;
  ReplenishFish(Resident);
  Check(PopulationGeneration==Generation,TEXT("duplicate reset cannot grant a second migration opportunity"));
  for(int32 Attempt=0;Attempt<120;++Attempt){
   ALureFish* Released=Fish[(Attempt%HabitatCount)*ResidentsPerHabitat];
   Released->Escape(true);ReplenishFish(Released);
  }
  int32 Totals[HabitatCount]={0,0,0};
  for(ALureFish* ResidentFish:Fish){
   if(IsValid(ResidentFish) && ResidentFish->HabitatIndex>=0 && ResidentFish->HabitatIndex<HabitatCount)
    ++Totals[ResidentFish->HabitatIndex];
  }
  Check(Fish.Num()>18 && Fish.Num()<=24 && Totals[0]<=8 && Totals[1]<=8 && Totals[2]<=8,
   TEXT("repeated sessions allow migration while population remains bounded"));
 }
 UE_LOG(LogTemp,Display,TEXT("LURE_POPULATION_TEST COMPLETE failures=%d"),Errors);
 FPlatformMisc::RequestExitWithStatus(false,Errors?1:0);
}

from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('#include "LureWorld.h"','#include "LureWorld.h"\n#include "FishingVisuals.h"\n#include "Engine/GameViewportClient.h"\n#include "GameFramework/PlayerInput.h"\n#include "InputKeyEventArgs.h"\n#include "Components/ExponentialHeightFogComponent.h"\n#include "Engine/ExponentialHeightFog.h"\n#include "Engine/PostProcessVolume.h"\n#include "EngineUtils.h"')
a=s.index(' Rod=CreateDefaultSubobject');b=s.index(' Lure=CreateDefaultSubobject',a)
s=s[:a]+''' Rig=CreateDefaultSubobject<USceneComponent>(TEXT("FishingRig")); Rig->SetupAttachment(Camera);
 Rig->SetRelativeLocation(FVector(40,20,-32)); Rig->SetRelativeRotation(FRotator(12,-10,0));
 auto Make=[&](const FString& Name,const TCHAR* Asset,USceneComponent* Parent){
  auto* M=CreateDefaultSubobject<UStaticMeshComponent>(*Name);M->SetupAttachment(Parent);
  M->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Asset));M->SetCollisionEnabled(ECollisionEnabled::NoCollision);return M;
 };
 Rod=Make(TEXT("RodHandle"),TEXT("/Game/LureArt/SM_RodHandle.SM_RodHandle"),Rig);
 RightArm=Make(TEXT("RightArm"),TEXT("/Game/LureArt/SM_RightArm.SM_RightArm"),Rig);
 LeftArm=Make(TEXT("LeftArm"),TEXT("/Game/LureArt/SM_LeftArm.SM_LeftArm"),Rig);
 LeftArm->SetRelativeLocation(FVector(-1,-7,-8));LeftArm->SetRelativeRotation(FRotator(0,-22,0));
 Crank=Make(TEXT("ReelCrank"),TEXT("/Game/LureArt/SM_ReelCrank.SM_ReelCrank"),Rig);Crank->SetRelativeLocation(FVector(-1,-2.8f,-7.5f));Crank->SetRelativeScale3D(FVector(1,-1,1));
 for(int i=0;i<16;++i){Blank.Add(Make(FString::Printf(TEXT("Blank%d"),i),TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),Rig));}
 for(int i=0;i<7;++i){Guides.Add(Make(FString::Printf(TEXT("Guide%d"),i),TEXT("/Game/LureArt/SM_Guide.SM_Guide"),Rig));}
 for(int i=0;i<24;++i){Line.Add(Make(FString::Printf(TEXT("Line%d"),i),TEXT("/Engine/BasicShapes/Cylinder.Cylinder"),RootComponent));}
 for(int i=0;i<3;++i){Ripples.Add(Make(FString::Printf(TEXT("Ripple%d"),i),TEXT("/Game/LureArt/SM_Guide.SM_Guide"),RootComponent));}
''' +s[b:]
s=s.replace('Camera->SetRelativeLocation(FVector(0,0,170));','Camera->SetFieldOfView(80); Camera->SetRelativeLocation(FVector(0,0,170));')
s=s.replace('Tint(Rod,FLinearColor(0.07f,0.09f,0.1f));','for(auto* B:Blank) Tint(B,FLinearColor(.015f,.021f,.024f));\n for(auto* L:Line) Tint(L,FLinearColor(.4f,.48f,.42f));')
s=s.replace('PC->SetInputMode(FInputModeGameOnly()); PC->bShowMouseCursor=false;','PC->PlayerCameraManager->ViewPitchMin=-75;PC->PlayerCameraManager->ViewPitchMax=70;')
s=s.replace(' ResetCast();\n if(FParse',' CaptureMouse();\n const FVector Homes[]={FVector(900,200,-65),FVector(1850,800,-95),FVector(2900,-500,-140),FVector(4100,1000,-100),FVector(5400,0,-120)};\n for(int i=0;i<5;++i){auto* F=GetWorld()->SpawnActor<ALureFish>();F->Initialize(Homes[i],i*2.7f);Fish.Add(F);}\n ResetCast();\n if(FParse',1)
s=s.replace(' I->BindKey(EKeys::Tab,IE_Pressed,this,&ALurePawn::SwitchLure);',' I->BindKey(EKeys::Tab,IE_Pressed,this,&ALurePawn::SwitchLure);\n I->BindKey(EKeys::V,IE_Pressed,this,&ALurePawn::ToggleObserve);\n I->BindKey(EKeys::Escape,IE_Pressed,this,&ALurePawn::ReleaseMouse);')
s=s.replace('AddControllerYawInput(V*0.7f);','if(!bObserve) AddControllerYawInput(V*0.16f);').replace('AddControllerPitchInput(-V*0.7f);','if(!bObserve) AddControllerPitchInput(-V*0.16f);')
s=s.replace('void ALurePawn::PressCast() { if','void ALurePawn::PressCast() { CaptureMouse(); if')
s=s.replace('if(Phase==EFishingPhase::Bite) {Stamina=1;', 'if(Phase==EFishingPhase::Bite && ActiveFish) {Stamina=1;')
s=s.replace('void ALurePawn::ResetCast(){ SetPhase','void ALurePawn::ResetCast(){ if(ActiveFish){ActiveFish->Escape();ActiveFish=nullptr;} if(bObserve)ToggleObserve(); SetPhase')
s=s.replace(' Notice=TEXT("Cast released");',' Charge=0; Notice=TEXT("Cast released");')
s=s.replace('const FVector Tip=Camera->GetComponentLocation()+Camera->GetForwardVector()*195+Camera->GetRightVector()*33;', 'UpdateRig(Dt);\n const FVector Tip=Rig->GetComponentTransform().TransformPosition(FVector(210,0,-Tension*42));')
s=s.replace('LurePosition.Z=0; SetPhase','LurePosition.Z=0; SplashPosition=LurePosition;SplashTime=Clock; SetPhase')
a=s.index('  else if(Phase==EFishingPhase::Retrieving) {');b=s.index(' } else if(Phase==EFishingPhase::Fighting)',a)
s=s[:a]+'''  else if(Phase==EFishingPhase::Bite && PhaseTime>1.3f){if(ActiveFish)ActiveFish->Escape();ActiveFish=nullptr;SetPhase(EFishingPhase::Retrieving); Notice=TEXT("Missed bite. The fish is retreating; try another pause.");}
'''+s[b:]
s=s.replace('Notice=TEXT("BASS LANDED! Released safely. Press R to cast again.");','Notice=TEXT("BASS LANDED! Press V to inspect, R to release.");')
a=s.index(' Lure->SetWorldLocation(LurePosition);');b=s.index('\nALureGameMode::ALureGameMode',a)
s=s[:a]+''' UpdateFish(Dt);
 Lure->SetWorldLocation(LurePosition);
 Lure->SetWorldRotation((GetActorLocation()-LurePosition).Rotation());
 if(bObserve && ActiveFish){
  FVector Focus=ActiveFish->GetActorLocation();FVector Eye=Focus+FVector(90,-145,55);
  Camera->SetWorldLocation(Eye);Camera->SetWorldRotation((Focus-Eye).Rotation());
 }else if(bObserve){FVector Eye=LurePosition+FVector(-120,-180,45);Camera->SetWorldLocation(Eye);Camera->SetWorldRotation((LurePosition-Eye).Rotation());}
 for(int i=0;i<Line.Num();++i){
  float A=float(i)/Line.Num(),B=float(i+1)/Line.Num();
  auto Point=[&](float T){return FMath::Lerp(Tip,LurePosition,T)-FVector(0,0,FMath::Sin(T*PI)*(Phase==EFishingPhase::Fighting?8:35));};
  FVector P=Point(A),Q=Point(B),D=Q-P;
  Line[i]->SetWorldLocation((P+Q)*.5f);Line[i]->SetWorldRotation(FRotationMatrix::MakeFromZ(D).Rotator());
  Line[i]->SetWorldScale3D(FVector(.0007f,.0007f,D.Size()/100));Line[i]->SetVisibility(Phase!=EFishingPhase::Landed);
 }
 for(int i=0;i<Ripples.Num();++i){
  const float Age=Clock-SplashTime-i*.15f;float Radius=8+Age*75;
  Ripples[i]->SetVisibility(Age>=0 && Age<1.8f);Ripples[i]->SetWorldLocation(SplashPosition+FVector(0,0,3+i*.15f));
  Ripples[i]->SetWorldRotation(FRotator(90,0,0));Ripples[i]->SetWorldScale3D(FVector(Radius,Radius,Radius*.07f));
 }
}
void ALurePawn::CaptureMouse(){
 if(auto* PC=Cast<APlayerController>(GetController())){
  FInputModeGameOnly Mode;Mode.SetConsumeCaptureMouseDown(false);PC->SetInputMode(Mode);PC->bShowMouseCursor=false;
  if(auto* VP=GetWorld()->GetGameViewport()){VP->SetMouseCaptureMode(EMouseCaptureMode::CapturePermanently_IncludingInitialMouseDown);VP->SetMouseLockMode(EMouseLockMode::LockAlways);}
 }
}
void ALurePawn::ReleaseMouse(){if(auto* PC=Cast<APlayerController>(GetController())){PC->SetInputMode(FInputModeGameAndUI());PC->bShowMouseCursor=true;Reeling=false;}}
void ALurePawn::ToggleObserve(){
 if(!bObserve && (Phase==EFishingPhase::Ready || Phase==EFishingPhase::Charging || Phase==EFishingPhase::Flying))return;
 bObserve=!bObserve;Camera->bUsePawnControlRotation=!bObserve;Rig->SetVisibility(!bObserve,true);
 if(!bObserve){Camera->SetRelativeLocation(FVector(0,0,170));Camera->SetRelativeRotation(FRotator::ZeroRotator);}
}
void ALurePawn::UpdateRig(float Dt){
 CrankAngle+=Reeling?Dt*600:0;
 float Kick=Phase==EFishingPhase::Flying?FMath::Exp(-PhaseTime*7)*18:0;
 Rig->SetRelativeRotation(FRotator(8+Charge*48-Kick-Tension*8,-12,0));
 Rig->SetRelativeLocation(FVector(40,20,-32+FMath::Sin(Clock*1.8f)*.25f));
 Crank->SetRelativeRotation(FRotator(0,0,CrankAngle));
 LeftArm->SetRelativeLocation(FVector(-1+FMath::Sin(FMath::DegreesToRadians(CrankAngle))*2.8f,-7,-8+FMath::Cos(FMath::DegreesToRadians(CrankAngle))*2.8f));
 for(int i=0;i<Blank.Num();++i){
  float A=float(i)/Blank.Num(),B=float(i+1)/Blank.Num();
  FVector P(18+A*192,0,-Tension*42*A*A),Q(18+B*192,0,-Tension*42*B*B),D=Q-P;
  Blank[i]->SetRelativeLocation((P+Q)*.5f);Blank[i]->SetRelativeRotation(FRotationMatrix::MakeFromZ(D).Rotator());
  float Radius=FMath::Lerp(.007f,.0013f,A);Blank[i]->SetRelativeScale3D(FVector(Radius,Radius,D.Size()/100+.001f));
 }
 for(int i=0;i<Guides.Num();++i){float A=float(i+1)/Guides.Num();Guides[i]->SetRelativeLocation(FVector(18+A*192,0,-Tension*42*A*A-1.2f));Guides[i]->SetRelativeScale3D(FVector(1-A*.7f));}
}
void ALurePawn::UpdateFish(float Dt){
 for(auto* F:Fish){
  if(F==ActiveFish && (Phase==EFishingPhase::Fighting || Phase==EFishingPhase::Bite)){F->SetHooked(LurePosition,Clock);continue;}
  if(F==ActiveFish && Phase==EFishingPhase::Landed){F->SetHooked(GetActorLocation()+FVector(60,0,90),Clock*.3f);continue;}
  bool Attack=F->Simulate(Dt,LurePosition,Phase==EFishingPhase::Retrieving,Clock-LastTwitch<1 || Reeling);
  if(Attack && Phase==EFishingPhase::Retrieving){ActiveFish=F;SetPhase(EFishingPhase::Bite);SplashPosition=LurePosition;SplashPosition.Z=0;SplashTime=Clock;Notice=TEXT("BITE! Press SPACE now!");}
 }
}
FString ALurePawn::FishStatus() const {
 for(auto* F:Fish)if(F->Behavior==EFishBehavior::Following || F->Behavior==EFishBehavior::Attacking)return TEXT("A bass is following your lure");
 return TEXT("Explore the fallen log and rocky shallows");
}
''' +s[b:]
s=s.replace('TEXT("Rock / fallen log area holds more fish.")','P->FishStatus()')
s=s.replace('TEXT("WILDWATER / LURE  -  MECHANICS PROTOTYPE")','TEXT("WILDWATER / LURE  -  LAKE BAY")')
s=s.replace('Wheel Adjust drag | Tab Change lure (before cast) | R Reset / Release | Alt+F4 Quit','Wheel Drag | Tab Lure | V Underwater / Inspect | R Release | Esc Cursor | Alt+F4 Quit')
s=s.replace('LurePosition=FVector(2000,0,0); SetPhase(EFishingPhase::Bite);','LurePosition=FVector(2000,0,0); ActiveFish=Fish[0]; SetPhase(EFishingPhase::Bite);')
p.write_text(s,encoding='utf-8')

from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
a=s.index('void ALureHUD::DrawHUD()');b=s.index('void ALurePawn::RunSmokeTest()',a);s=s[:a]+s[b:]
s=s.replace('RightArm=Make(TEXT("RightArm"),TEXT("/Game/LureArt/SM_RightArm.SM_RightArm")','RightArm=Make(TEXT("RightArm"),TEXT("/Game/LureArt/SM_LeftArm.SM_LeftArm")').replace('LeftArm=Make(TEXT("LeftArm"),TEXT("/Game/LureArt/SM_LeftArm.SM_LeftArm")','LeftArm=Make(TEXT("LeftArm"),TEXT("/Game/LureArt/SM_RightArm.SM_RightArm")')
s=s.replace('LeftArm->SetRelativeRotation(FRotator(0,-22,0))','LeftArm->SetRelativeRotation(FRotator::ZeroRotator)').replace('Crank->SetRelativeScale3D(FVector(1,-1,1))','Crank->SetRelativeScale3D(FVector::OneVector)')
s=s.replace('LeftArm->SetRelativeLocation(FVector(-1+FMath::Sin(FMath::DegreesToRadians(CrankAngle))*2.8f,-7,-8+FMath::Cos(FMath::DegreesToRadians(CrankAngle))*2.8f));','float A=FMath::DegreesToRadians(CrankAngle);\n LeftArm->SetRelativeLocation(FVector(3.8f,-6.9f*FMath::Cos(A)+3.1f*FMath::Sin(A),-7.5f-6.9f*FMath::Sin(A)-3.1f*FMath::Cos(A)));')
s=s.replace('Lure->SetStaticMesh(Shape(TEXT("Sphere"))); Lure->SetWorldScale3D(FVector(0.12f,0.045f,0.045f));','Lure->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Minnow.SM_Minnow")));')
s=s.replace(' Tint(Lure,FLinearColor(1,0.45f,0.03f));','')
s=s.replace('F->Initialize(Homes[i],i*2.7f);Fish.Add(F);','F->Initialize(Homes[i],i*2.7f);F->SetSpecies(i%4);Fish.Add(F);')
s=s.replace(' ResetCast();\n if(FParse',' ResetCast();\n SessionInit();\n if(FParse',1)
s=s.replace('void ALurePawn::PressCast() { CaptureMouse();','void ALurePawn::PressCast() { if(bMenuOpen)return; CaptureMouse();')
s=s.replace('void ALurePawn::ReelStart(){Reeling=true;}','void ALurePawn::ReelStart(){if(!bMenuOpen)Reeling=true;}')
s=s.replace('void ALurePawn::Strike() {','void ALurePawn::Strike() {\n if(bMenuOpen)return;')
s=s.replace('if(!bObserve) AddControllerYawInput(V*0.16f)','if(!bObserve && !bMenuOpen) AddControllerYawInput(V*Sensitivity)').replace('if(!bObserve) AddControllerPitchInput(-V*0.16f)','if(!bObserve && !bMenuOpen) AddControllerPitchInput(-V*Sensitivity)')
s=s.replace('SetPhase(EFishingPhase::Flying); Notice','SetPhase(EFishingPhase::Flying); PlayCue(TEXT("Cast")); Notice')
s=s.replace('SetPhase(EFishingPhase::Flying); Charge=0;', 'SetPhase(EFishingPhase::Flying); PlayCue(TEXT("Cast")); Charge=0;')
s=s.replace('SplashTime=Clock; SetPhase(EFishingPhase::Retrieving);','SplashTime=Clock; PlayCue(TEXT("Splash")); SetPhase(EFishingPhase::Retrieving);')
s=s.replace('SetPhase(EFishingPhase::Landed); Notice','SetPhase(EFishingPhase::Landed); RecordCatch(); Notice')
s=s.replace('SplashTime=Clock;Notice=TEXT("BITE!', 'SplashTime=Clock;PlayCue(TEXT("Bite"));Notice=TEXT("BITE!')
s=s.replace('if(Phase==EFishingPhase::Ready){LureType=1-LureType; Notice=TEXT("Lure changed");}', '''if(Phase==EFishingPhase::Ready && !bMenuOpen){LureType=(LureType+1)%5;
 const TCHAR* Names[]={TEXT("SM_Minnow"),TEXT("SM_SoftBait"),TEXT("SM_Spinner"),TEXT("SM_Popper"),TEXT("SM_Jig")};
 Lure->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,*FString::Printf(TEXT("/Game/LureArt/%s.%s"),Names[LureType],Names[LureType])));Notice=LureName();}''')
s=s.replace(' Super::Tick(Dt); FrameDelta=Dt; Clock+=Dt; PhaseTime+=Dt;', ''' Super::Tick(Dt); FrameDelta=Dt; Clock+=Dt;
 UpdateEnvironment(Dt);
 if(FParse::Param(FCommandLine::Get(),TEXT("LureSessionTest")) && Clock>1 && Clock-Dt<=1)RunSessionTest();
 if(bMenuOpen){Reeling=false;for(auto* L:Line)L->SetVisibility(false);return;}
 PhaseTime+=Dt;''')
s=s.replace('if(Reeling) LurePosition+=Toward.GetSafeNormal()*(LureType==0?200.f:140.f)*Dt;', 'const float Speeds[]={180.f,120.f,220.f,110.f,100.f};\n  if(Reeling) LurePosition+=Toward.GetSafeNormal()*Speeds[LureType]*Dt;')
a=s.index('  const float TargetDepth=');b=s.index('  if(Clock-LastTwitch',a)
s=s[:a]+'''  if(LureType==0)LurePosition.Z=FMath::FInterpTo(LurePosition.Z,Reeling?-80.f:-25.f,Dt,1.5f);
  else if(LureType==3)LurePosition.Z=2+FMath::Sin(Clock*3)*1.5f;
  else {float Sink=LureType==4?75.f:(LureType==1?35.f:45.f);LurePosition.Z=FMath::Clamp(LurePosition.Z+Dt*(Reeling?30.f:-Sink),-340.f,-8.f);}
  Depth=FMath::Max(0.f,-LurePosition.Z/100);
''' +s[b:]
a=s.index('void ALurePawn::ReleaseMouse()');b=s.index('\nvoid ALurePawn::ToggleObserve',a)
s=s[:a]+'''void ALurePawn::ReleaseMouse(){
 if(bMenuOpen){if(bStarted)MenuAction(TEXT("play"));return;}
 bMenuOpen=true;MenuPage=0;Reeling=false;Rig->SetVisibility(false,true);SaveSession();
 if(auto* PC=Cast<APlayerController>(GetController())){PC->SetInputMode(FInputModeGameAndUI());PC->bShowMouseCursor=true;}
}''' +s[b:]
s=s.replace('TEXT("A bass is following your lure")','TEXT("有鱼正在追饵，试试停顿或轻抽")').replace('TEXT("Explore the fallen log and rocky shallows")','TEXT("留意沉木与石边，改变收线节奏")')
s=s.replace('bool Attack=F->Simulate','F->Activity=(Weather==3?1.2f:1.f)*(TimeOfDay==0||TimeOfDay==2?1.15f:.8f)*(LureType==F->Species%5?1.3f:1.f);\n  bool Attack=F->Simulate')
# Replace tree cones with instanced authored trees, preserving their material slots.
a=s.index(' auto* Trunks=Instances(');b=s.index(' FRandomStream Rng',a)
s=s[:a]+''' auto* Trees=Instances(TEXT("Forest"),LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Birch.SM_Birch")),FLinearColor(.04f,.08f,.03f));
 Trees->EmptyOverrideMaterials();
''' +s[b:]
a=s.index('  Trunks->AddInstance');b=s.index('\n }\n for(int i=0;i<30',a)
s=s[:a]+'''  Trees->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),FVector(X,Y,Far?-50:65),FVector(H/850)),true);
''' +s[b:]
s=s.replace('auto* Shore=Place(GetWorld(),TEXT("Cube"),FVector(-1800,0,-70),FVector(36,180,2.8f),FLinearColor(.12f,.14f,.06f));','auto* Shore=Place(GetWorld(),TEXT("Cube"),FVector::ZeroVector,FVector::OneVector,FLinearColor(.12f,.14f,.06f));\n Shore->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Bank.SM_Bank")));')
s=s.replace('Post->Settings.MotionBlurAmount=0;','Post->Settings.MotionBlurAmount=0;\n if(auto* P=Cast<ALurePawn>(UGameplayStatics::GetPlayerPawn(this,0)))P->ApplyEnvironment();')
s=s.replace('#include "LureWorld.h"','#include "LureWorld.h"\n#include "Kismet/GameplayStatics.h"')
p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/FishingVisuals.h');s=p.read_text(encoding='utf-8-sig').replace('float SizeFactor=1,Weight=1;','float SizeFactor=1,Weight=1,Activity=1;');p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/FishingVisuals.cpp');s=p.read_text(encoding='utf-8-sig').replace('Curiosity+=Dt*(Twitch?1.7f:.65f)','Curiosity+=Dt*Activity*(Twitch?1.7f:.65f)');p.write_text(s,encoding='utf-8')

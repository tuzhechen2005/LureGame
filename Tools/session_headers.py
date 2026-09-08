from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.h');s=p.read_text(encoding='utf-8-sig')
s=s.replace('class ALureFish;','class ALureFish;\nclass ULureSave;\nclass UAudioComponent;\nclass UFont;')
s=s.replace('FString FishStatus() const;','''FString FishStatus() const;
 bool bMenuOpen=false,bStarted=false;
 int32 MenuPage=0,Weather=0,TimeOfDay=0,Spot=0;
 float Sensitivity=.16f,Volume=.65f;
 FString LastCatch;
 UPROPERTY() ULureSave* SaveData;
 void SessionInit();
 void SaveSession();
 void MenuAction(const FString& Action);
 void ApplyEnvironment();
 void UpdateEnvironment(float Dt);
 void RecordCatch();
 void PlayCue(const TCHAR* Name);
 FString LureName() const;
 FString WeatherName() const;
 FString TimeName() const;
 FString SpotName() const;
 void RunSessionTest();
''')
s=s.replace('UPROPERTY() UCameraComponent* Camera;','''UPROPERTY() UCameraComponent* Camera;
 UPROPERTY() UAudioComponent* AmbientAudio;
 UPROPERTY() UAudioComponent* ReelAudio;
 UPROPERTY() class UInstancedStaticMeshComponent* Rain;
''')
s=s.replace('virtual void DrawHUD() override;','virtual void DrawHUD() override;\nprivate:\n UPROPERTY() UFont* ChineseFont;')
p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/FishingVisuals.h');s=p.read_text(encoding='utf-8-sig').replace('FVector Home;','FVector Home;\n int32 Species=0;\n float SizeFactor=1,Weight=1;\n void SetSpecies(int32 Type);\n FString SpeciesName() const;');p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/FishingVisuals.cpp');s=p.read_text(encoding='utf-8-sig');s=s.replace('SetActorLocation(MouthPosition-FVector(20,0,0));','')
s=s.replace('Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Time*20)*32,0));','SetActorLocation(MouthPosition-GetActorForwardVector()*20*SizeFactor);\n Tail->SetRelativeRotation(FRotator(0,FMath::Sin(Time*20)*32,0));')
s+='''
void ALureFish::SetSpecies(int32 Type){
 Species=Type%4;
 const TCHAR* Paths[]={TEXT("/Game/LureArt/SM_BassBody.SM_BassBody"),TEXT("/Game/LureArt/SM_PerchBody.SM_PerchBody"),TEXT("/Game/LureArt/SM_PikeBody.SM_PikeBody"),TEXT("/Game/LureArt/SM_TroutBody.SM_TroutBody")};
 Body->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,Paths[Species]));
 SizeFactor=.8f+FMath::Frac(Seed*.719f+.31f)*.55f;
 const float Base[]={1.5f,.45f,3.2f,1.15f};Weight=Base[Species]*FMath::Pow(SizeFactor,3.f);
 SetActorScale3D(FVector(SizeFactor));
 const float TailX[]={-22.5f,-15.3f,-33.75f,-21.4f};Tail->SetRelativeLocation(FVector(TailX[Species],0,0));
}
FString ALureFish::SpeciesName() const { const TCHAR* Names[]={TEXT("大口黑鲈"),TEXT("河鲈"),TEXT("白斑狗鱼"),TEXT("虹鳟")};return Names[Species];}
''';p.write_text(s,encoding='utf-8')
p=Path('D:/LureGame/Source/LureGame/LureGame.Build.cs');s=p.read_text(encoding='utf-8-sig').replace('"InputCore"','"InputCore", "SlateCore"');p.write_text(s,encoding='utf-8')

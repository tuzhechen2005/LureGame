from pathlib import Path
p=Path('D:/LureGame/Config/DefaultEngine.ini');s=p.read_text(encoding='utf-8-sig')
Path('D:/LureGame/ArtDirection/Renderer-before-concept.ini').write_text(s,encoding='utf-8')
s=s.replace('r.DynamicGlobalIlluminationMethod=0','r.DynamicGlobalIlluminationMethod=1').replace('r.ReflectionMethod=2','r.ReflectionMethod=1').replace('r.AntiAliasingMethod=2','r.AntiAliasingMethod=4').replace('r.Shadow.Virtual.Enable=0','r.Shadow.Virtual.Enable=1\nr.GenerateMeshDistanceFields=True\nr.Lumen.TranslucencyReflections.FrontLayer.EnableForProject=True')
p.write_text(s,encoding='utf-8-sig')
p=Path('D:/LureGame/Source/LureGame/LureSession.cpp');s=p.read_text(encoding='utf-8-sig');s=s.replace('\n ApplyEnvironment();\n}\nvoid ALurePawn::SaveSession()', '\n auto* Graphics=UGameUserSettings::GetGameUserSettings();Graphics->SetOverallScalabilityLevel(FMath::Clamp(SaveData->Quality,0,2));Graphics->SetFrameRateLimit(60);Graphics->ApplyNonResolutionSettings();\n ApplyEnvironment();\n}\nvoid ALurePawn::SaveSession()');p.write_text(s,encoding='utf-8-sig')

from pathlib import Path
p=Path('D:/LureGame/Source/LureGame/LureWorld.cpp');s=p.read_text(encoding='utf-8-sig')
s=s.replace('Trees->EmptyOverrideMaterials();','Trees->EmptyOverrideMaterials(); Rocks->EmptyOverrideMaterials();')
start=s.index(' // Reeds at the waterline, instanced to keep draw calls low.')
end=s.index(' auto* Sun=',start)
s=s[:start]+''' // Textured grass clumps have individual blades and cutout leaf edges.
 auto* Grass=Instances(TEXT("BankGrass"),LoadObject<UStaticMesh>(nullptr,TEXT("/Game/LureArt/SM_Grass.SM_Grass")),FLinearColor::White);
 Grass->EmptyOverrideMaterials();
 for(int i=0;i<1500;++i){float X=Rng.FRandRange(-1450,-80),Y=Rng.FRandRange(-4500,4500);if(X>-650 && FMath::Abs(Y)<240)continue;float S=Rng.FRandRange(.6f,1.6f);Grass->AddInstance(FTransform(FRotator(0,Rng.FRandRange(0,360),0),FVector(X,Y,45),FVector(S)),true);}
''' +s[end:]
p.write_text(s,encoding='utf-8-sig')
credit=Path('D:/LureGame/Docs/Credits.md')
credit.write_text('''# Asset credits

Powered by Poly Haven — https://polyhaven.com

The following source scans and textures are CC0, downloaded through the Poly Haven public API:
- https://polyhaven.com/a/rock_moss_set_01
- https://polyhaven.com/a/tree_small_02
- https://polyhaven.com/a/grass_medium_01

Models were reduced, repositioned and converted for this game. Source downloads and material mappings are retained in ArtSource/Nature and ArtSource/Realistic.

Fishing equipment, hand geometry, fish geometry, water and gameplay are project-authored. Unreal Engine built-in sky and primitives remain subject to Epic's engine license. The DroidSansFallback font is distributed under Apache 2.0; see Apache-2.0.txt.
''',encoding='utf-8')

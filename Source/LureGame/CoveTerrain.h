#pragma once
#include "CoreMinimal.h"
namespace Cove {
inline float ShoreX(float Y) { return 3500.f-3500.f*FMath::Sqrt(FMath::Max(0.f,1.f-FMath::Square(Y/5600.f))); }
inline float Height(float X,float Y) {
 const float R=FMath::Sqrt(FMath::Square((X-3500.f)/3500.f)+FMath::Square(Y/5600.f));
 const float D=(R-1.f)*3500.f;
 if(D<0) return FMath::Max(-580.f,D*.30f);
 const float Fade=FMath::Clamp(D/800.f,0.f,1.f);
 const float Hill=1000.f*FMath::Exp(-FMath::Square((X-9500.f)/4200.f)-FMath::Square((Y+4500.f)/5000.f));
 return FMath::Min(D*.12f,450.f)+Fade*(Hill+65.f*FMath::Sin(X*.0012f)*FMath::Cos(Y*.0009f)+18.f*FMath::Sin(X*.0041f+Y*.0023f));
}
}

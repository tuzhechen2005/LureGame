#pragma once
#include "CoreMinimal.h"

enum class EFightMove : uint8 { Recover, RunLeft, RunRight, Dive, HeadShake, Jump };
struct FFightInput {
 bool bReeling=false;
 float Drag=.5f;
 float RodSide=0; // -1 left, +1 right
 float RodLift=0; // -1 lowered, +1 lifted
};
struct FFishingFight {
 EFightMove Move=EFightMove::Recover;
 float Tension=.4f,Energy=1,LineCondition=1,HookSecurity=1,Distance=20;
 float Time=0,MoveTime=0,MoveDuration=3,Pull=.5f,Control=0,CleanSeconds=0;
 float LateralOffset=0,JumpHeight=0,Strength=1;
 int32 MoveIndex=0,Seed=0;
 bool bBroken=false,bLost=false;
 void Start(float Weight,int32 Species,float HookQuality,float DistanceMetres);
 void Step(float Dt,const FFightInput& Input);
 bool IsSurging() const;
 bool IsTelegraphing() const;
 float RequiredSide() const;
 FString MoveName() const;
 FString Instruction() const;
private:
 void AdvanceMove();
};

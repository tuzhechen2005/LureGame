using UnrealBuildTool;
public class LureGameTarget : TargetRules {
 public LureGameTarget(TargetInfo Target) : base(Target) {
  Type = TargetType.Game;
  DefaultBuildSettings = BuildSettingsVersion.V7;
  IncludeOrderVersion = EngineIncludeOrderVersion.Unreal5_8;
  ExtraModuleNames.Add("LureGame");
 }
}


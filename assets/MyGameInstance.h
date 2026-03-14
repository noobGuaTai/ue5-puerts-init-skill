#pragma once

#include "JsEnv.h"
#include "CoreMinimal.h"
#include "Engine/GameInstance.h"
#include "MyGameInstance.generated.h"

// Replace YOURPROJECT_API with your project's API macro (defined in [ProjectName].Build.cs)
UCLASS()
class YOURPROJECT_API UMyGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	virtual void Init() override;

	virtual void OnStart() override;

	virtual void Shutdown() override;

private:
	TSharedPtr<puerts::FJsEnv> GameScript;
};

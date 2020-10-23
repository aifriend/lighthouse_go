#pragma once



struct TD2020_API FTD2020FloatingCombatTextData
{
    /** Text to display. */
    FString Text;

    /** Color to display the text with. */
    FLinearColor Color;

    /** Scale to display the text with. */
    float Scale;

    /** Total time to show the text on screen before removing it. */
    float Lifetime;

    /** Remaining time to show the text on screen before removing it. */
    float RemainingLifetime;
};

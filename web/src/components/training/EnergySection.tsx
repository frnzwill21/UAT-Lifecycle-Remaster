import { Zap } from "lucide-react";
import { Input } from "../ui/input";
import type { Config, UpdateConfigType } from "@/types";
import Tooltips from "@/components/_c/Tooltips";

type Props = {
  config: Config;
  updateConfig: UpdateConfigType;
};

export default function TrainingSection({ config, updateConfig }: Props) {
  const {
    maximum_failure,
    minimum_condition_severity,
    skip_training_energy,
    never_rest_energy,
    skip_infirmary_unless_missing_energy,
    rest_before_summer_energy,
  } = config;

  return (
    <div className="section-card">
      <h2 className="text-3xl font-semibold mb-6 flex items-center gap-3">
        <Zap className="text-primary" />
        Energy
      </h2>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-2">
        <div className="flex flex-col gap-2">
          <label className="flex flex-row gap-2 w-fit items-center cursor-pointer">
            Skip Training Energy
            <Input
              className="w-20 text-center"
              type="number"
              min={0}
              value={skip_training_energy}
              onChange={(e) => updateConfig("skip_training_energy", e.target.valueAsNumber)} /><Tooltips>This options makes the bot skip doing the training if energy is below this value. It does not skip the training check. There may be exceptions to this rule like high energy gain from wit training.</Tooltips>
          </label>
          <label className="flex flex-row gap-2 w-fit items-center cursor-pointer">
            Never Rest Energy
            <Input
              className="w-20 text-center"
              type="number"
              min={0}
              value={never_rest_energy}
              onChange={(e) => updateConfig("never_rest_energy", e.target.valueAsNumber)} /><Tooltips>This will disable the bot's rest ability if the energy is above this value. If this conflicts with skip training energy bot will get stuck.</Tooltips>
          </label>
        </div>
        <div className="flex flex-col gap-2">
          <label className="flex flex-row gap-2 w-fit items-center cursor-pointer">
            Rest Before Summer Energy
            <Input
              className="w-20 text-center"
              type="number"
              min={0}
              value={rest_before_summer_energy}
              onChange={(e) =>
                updateConfig("rest_before_summer_energy", e.target.valueAsNumber)
              }
            /><Tooltips>Right before summer bot will try to rest if energy is below this value. If there's a career race in late jun bot will try to rest in early jun if energy is below the value.</Tooltips>
          </label>
          <label className="flex flex-row gap-2 w-fit items-center cursor-pointer">
            Skip Infirmary Threshold
            <Input
              className="w-20 text-center"
              type="number"
              min={0}
              value={skip_infirmary_unless_missing_energy}
              onChange={(e) =>
                updateConfig(
                  "skip_infirmary_unless_missing_energy",
                  e.target.valueAsNumber
                )
              }
            /><Tooltips>The bot will try to skip infirmary if it's not missing at least this amount of energy. There are conditions that are considered severe which will override this behavior.</Tooltips>
          </label>
        </div>

        <div className="flex flex-col gap-2">
          <label className="flex flex-row gap-2 w-fit items-center cursor-pointer">
            Base Failure Chance (%)
            <div className="flex items-center gap-2">
              <Input
                className="w-20 text-center"
                type="number"
                min={0}
                value={maximum_failure}
                onChange={(e) =>
                  updateConfig(
                    "maximum_failure",
                    isNaN(e.target.valueAsNumber) ? 0 : e.target.valueAsNumber
                  )
                }
              />
            </div><Tooltips>This is the base failure chance that the bot is willing to accept. This is further modified in Timeline section with the risk taking values.</Tooltips>
          </label>
          <label className="flex flex-row gap-2 w-fit items-center cursor-pointer">
            Min Condition Severity
            <Input
              className="w-20 text-center"
              type="number"
              step={1}
              value={minimum_condition_severity}
              onChange={(e) =>
                updateConfig(
                  "minimum_condition_severity",
                  e.target.valueAsNumber
                )
              }
            /><Tooltips>{"This is the minimum condition severity for the bot to be forced into the infirmary.\n\
            Bad status effect values are 2 for slacker and 1 for other effects.\n\
            If there's two bad statuses that is 1 and this value is set to 2 bot will still be forced into the infirmary."}</Tooltips>
          </label>
        </div>
      </div>
    </div>
  );
}

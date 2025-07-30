import { getIndicatorDataScript, getParams } from "../dom.mjs";
import { getToolTip, makeChart, setBackgroundInDatasets } from "../utils.mjs";

import { COLORS } from "../enums.mjs";
import { addEmptyGraphMessage } from "./utils.mjs";
import { formatIndicatorValue } from "../format.mjs";

function getPlugins(indicator) {
    return {
        datalabels: {
            display: true,
            color: (context) => {
                const bgColor = context.dataset.backgroundColor;
                return COLORS[bgColor] || "white";
            },
            anchor: "center",
            align: "center",
            font: {
                weight: "bold",
            },
            formatter: (value) =>
                `${formatIndicatorValue(value)} ${indicator.unite}`,
        },
        tooltip: getToolTip(indicator.unite),
    };
}

function makeProportionsChart(indicator) {
    const { territory_name: label } = getParams();

    const ctx = document.getElementById("proportionsChart");
    if (ctx === null) {
        return;
    }

    const proportionsData = getIndicatorDataScript(indicator, "proportions");
    if (!proportionsData) {
        return;
    }

    const datasets = proportionsData.values;

    const emptyDatasets = datasets
        .map((ds) => ds.data)
        .flat()
        .every((d) => d === null);
    if (datasets.length === 0 || emptyDatasets) {
        addEmptyGraphMessage(ctx);
        return;
    }

    setBackgroundInDatasets(datasets);

    const data = {
        labels: [label],
        datasets,
    };
    const options = {
        indexAxis: "y",
        maintainAspectRatio: false,
        plugins: getPlugins(indicator),
        scales: {
            x: {
                display: false,
                stacked: true,
            },
            y: {
                display: false,
                stacked: true,
            },
        },
    };

    makeChart(ctx, "bar", data, options);
}

export { makeProportionsChart };

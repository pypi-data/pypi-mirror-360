from .utils import should_run_landTransformationFromCropland, run_landTransformationFromCropland

REQUIREMENTS = {
    "ImpactAssessment": {
        "endDate": "",
        "country": {"@type": "Term", "termType": "region"},
        "emissionsResourceUse": [{
            "@type": "Indicator",
            "term.@id": "landTransformation20YearAverageDuringCycle",
            "value": "",
            "previousLandCover": {
                "@type": "Term",
                "termType": "landCover",
                "@id": "cropland"
            }
        }]
    }
}
LOOKUPS = {
    "region-faostatArea": ""
}
RETURNS = {
    "Indicator": [{
        "value": "",
        "landCover": "",
        "previousLandCover": ""
    }]
}
TERM_ID = 'landTransformation20YearAverageDuringCycle'


def run(impact: dict):
    should_run, indicators = should_run_landTransformationFromCropland(TERM_ID, impact)
    return run_landTransformationFromCropland(TERM_ID, impact, indicators, 20) if should_run else []

export enum FeatureType {
    NUMERIC = 1,
    CATEGORICAL = 2,
    NONE = 3
}


export class FeatureLabel {
    public featureType: FeatureType;
    public caption: string = "";

    constructor(featureType: FeatureType = FeatureType.NONE) {
        this.featureType = featureType;
        this.setCaption();
    }

    switchType() : void {
        if (this.featureType != FeatureType.NONE) {
            this.featureType = this.featureType == FeatureType.NUMERIC ? FeatureType.CATEGORICAL : FeatureType.NUMERIC;
            this.setCaption();
        }
    }

    isNumeric() : boolean {
        return this.featureType == FeatureType.NUMERIC;
    }

    isCategorical() : boolean {
        return this.featureType == FeatureType.CATEGORICAL;
    }

    private setCaption() : void {
        switch (this.featureType) {
            case FeatureType.NUMERIC:
                this.caption = "N";
                break;
            case FeatureType.CATEGORICAL:
                this.caption = "C";
                break;
            case FeatureType.NONE:
                this.caption = "";
                break;
        }
    }
}
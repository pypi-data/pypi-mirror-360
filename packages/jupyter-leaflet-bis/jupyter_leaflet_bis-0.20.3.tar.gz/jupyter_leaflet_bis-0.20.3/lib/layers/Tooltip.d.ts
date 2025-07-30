import { WidgetView } from '@jupyter-widgets/base';
import { Tooltip } from 'leaflet';
import { ILeafletLayerModel, LeafletUILayerModel, LeafletUILayerView } from './Layer';
interface ILeafletTooltipModel extends ILeafletLayerModel {
    _view_name: string;
    _model_name: string;
    location: number[] | null;
}
export declare class LeafletTooltipModel extends LeafletUILayerModel {
    defaults(): ILeafletTooltipModel;
}
export declare class LeafletTooltipView extends LeafletUILayerView {
    obj: Tooltip;
    initialize(parameters: WidgetView.IInitializeParameters<LeafletTooltipModel>): void;
    create_obj(): void;
    model_events(): void;
}
export {};
//# sourceMappingURL=Tooltip.d.ts.map
// Copyright (c) Jupyter Development Team.
// Distributed under the terms of the Modified BSD License.
import L from '../leaflet';
import { LeafletUILayerModel, LeafletUILayerView, } from './Layer';
export class LeafletTooltipModel extends LeafletUILayerModel {
    defaults() {
        return {
            ...super.defaults(),
            _view_name: 'LeafletMarkerView',
            _model_name: 'LeafletMarkerModel',
            location: null,
        };
    }
}
export class LeafletTooltipView extends LeafletUILayerView {
    initialize(parameters) {
        super.initialize(parameters);
    }
    create_obj() {
        if (this.model.get('location')) {
            // Stand-alone tooltip
            this.obj = L.tooltip(this.model.get('location'), this.get_options());
        }
        else {
            this.obj = L.tooltip(this.get_options());
        }
    }
    model_events() {
        super.model_events();
        this.listenTo(this.model, 'change:location', () => {
            if (this.model.get('location')) {
                this.obj.setLatLng(this.model.get('location'));
                this.send({
                    event: 'move',
                    location: this.model.get('location'),
                });
            }
        });
        this.listenTo(this.model, 'change:content', () => {
            this.obj.setContent(this.model.get('content'));
        });
    }
}
//# sourceMappingURL=Tooltip.js.map
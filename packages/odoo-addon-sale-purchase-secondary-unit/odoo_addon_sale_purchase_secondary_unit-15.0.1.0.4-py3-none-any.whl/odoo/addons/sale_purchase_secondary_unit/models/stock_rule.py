# Copyright 2023 Tecnativa - Sergio Teruel
# Copyright 2023 Tecnativa - Carlos Dauden
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl)

from odoo import api, models


class StockRule(models.Model):
    _inherit = "stock.rule"

    @api.model
    def _get_procurements_to_merge_groupby(self, procurement):
        """Do not group purchase order line if they have different secondary_uom in
        sale order line.
        """
        return (
            procurement.values.get("secondary_uom_id"),
            super(StockRule, self)._get_procurements_to_merge_groupby(procurement),
        )

    @api.model
    def _run_buy(self, procurements):
        return super(
            StockRule, self.with_context(skip_default_secondary_uom_qty=True)
        )._run_buy(procurements)

    def _update_purchase_order_line(
        self, product_id, product_qty, product_uom, company_id, values, line
    ):
        vals = super()._update_purchase_order_line(
            product_id, product_qty, product_uom, company_id, values, line
        )
        if values.get("secondary_uom_id", False):
            moves_dest = line.move_dest_ids + values.get(
                "move_dest_ids", self.env["stock.move"]
            )
            moves = self.env["stock.move"].browse(
                list(moves_dest._rollup_move_dests(set()))
            )
            cancelled_so_lines = self.env.context.get("cancelled_so_lines", [])
            sale_lines = moves.mapped("sale_line_id").filtered(
                lambda ln: ln.id not in cancelled_so_lines
            )
            vals["secondary_uom_qty"] = sum(sale_lines.mapped("secondary_uom_qty"))
        return vals

    @api.model
    def get_stock_move_sale_line(self, stock_move):
        for move in stock_move.move_dest_ids:
            if move.sale_line_id:
                return move.sale_line_id
            return self.get_stock_move_sale_line(move)

    @api.model
    def _merge_procurements(self, procurements_to_merge):
        # The quantity accumulation is embedded in this method and is not heritable
        # Avoid process only one procurement
        if len(procurements_to_merge) == 1 and len(procurements_to_merge[0]) == 1:
            return super()._merge_procurements(procurements_to_merge)
        secondary_index_dic = {}
        # Fill dict with total secondary_uom_qty by group of procurements to merge
        for index, procurements in enumerate(procurements_to_merge):
            secondary_index_dic[index] = 0
            for procurement in procurements:
                secondary_index_dic[index] += procurement.values.get(
                    "secondary_uom_qty", 0
                )
        merged_procurements = super()._merge_procurements(procurements_to_merge)
        # Set total secondary_uom_qty from previous dict
        for index, merged_procurement in enumerate(merged_procurements):
            merged_procurement.values["secondary_uom_qty"] = secondary_index_dic[index]
        return merged_procurements

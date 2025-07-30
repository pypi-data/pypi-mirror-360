# Copyright 2025 ForgeFlow S.L. (https://www.forgeflow.com)
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
from openupgradelib import openupgrade, openupgrade_merge_records


def merge_ogone_sips_into_worldline(env):
    ogone = env["payment.provider"].search([("code", "=", "ogone")], limit=1)
    sips = env.ref("payment.payment_provider_sips")
    worldline = env.ref("payment.payment_provider_worldline")
    to_merge = []
    if ogone:
        to_merge.append(ogone.id)
    if sips:
        to_merge.append(sips.id)
    if to_merge:
        openupgrade_merge_records.merge_records(
            env,
            "payment.provider",
            to_merge,
            worldline.id,
            {"openupgrade_other_fields": "preserve"},
            delete=False,
        )


@openupgrade.migrate()
def migrate(env, version):
    merge_ogone_sips_into_worldline(env)
    openupgrade.load_data(env, "payment", "18.0.2.0/noupdate_changes_manual.xml")
    openupgrade.load_data(env, "payment", "18.0.2.0/noupdate_changes.xml")
    openupgrade.delete_records_safely_by_xml_id(env, ["payment.payment_provider_sips"])

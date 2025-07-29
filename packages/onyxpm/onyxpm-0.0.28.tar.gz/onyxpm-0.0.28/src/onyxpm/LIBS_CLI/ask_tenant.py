from CLASSES.NxTenant import NxTenant

def ask_tenant(message):
    tenants = [
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="5", tenant_name ='ADS', username ="api@alchimiedatasolutions.com", password ="Dense?Zookeeper?Twenty4"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="12", tenant_name ='BLUETEK', username ="api@alchimiedatasolutions.com", password ="Crown4?Armless?Chivalry"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="6", tenant_name ='HBE', username ="api@alchimiedatasolutions.com", password ="Scrabble?Pulsate?Showcase6"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="10", tenant_name ='HBE_PREPROD', username ="api@alchimiedatasolutions.com", password ="Livestock-Spoken6-Harmful"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="7", tenant_name ='HBE_PROD', username ="api@alchimiedatasolutions.com", password ="Overnight2-Fantasy-Recopy"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="11", tenant_name ='MET_UAT', username ="api@alchimiedatasolutions.com", password ="Unwatched9?Mangle?Veto"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="16", tenant_name ='MET_PROD', username ="api@alchimiedatasolutions.com", password ="Untitled-Upturned4-Peculiar"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="4", tenant_name ='SLOGIA', username ="api@alchimiedatasolutions.com", password ="Stuffing-Tiptop5-Chaplain"),
        NxTenant(domain ="https://onyx-back.azurewebsites.net", tenant_id ="14", tenant_name ='TERRA LACTA', username ="api@alchimiedatasolutions.com", password ="Quizzical-Propose-Dayroom1"),
    ]
    print(message)
    line = ""
    i = 0
    print("")
    for tnt in tenants:
        i += 1
        line += ("Id : {} Name : {}".format(tnt.tenant_id.ljust(5), tnt.tenant_name)).ljust(55)
        if i == 4:
            print(line)
            line = ""
            i = 0
    if i > 0:
        print(line)
    id = input("\nPlease, type the tenant id: ")

    for tnt in [x for x in tenants if x.tenant_id == str(id)]:
        tenant = tnt
    print("\nTenant \"{}\" has been selected.\n".format(tenant.tenant_name))
    return tenant
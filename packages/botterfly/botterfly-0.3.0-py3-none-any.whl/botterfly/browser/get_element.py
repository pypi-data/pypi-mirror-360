def get_element(page, selector):
    by = selector["by"]
    value = selector["value"]

    match by:
        case "alt_text":
            return page.get_by_alt_text(value)
        case "label":
            return page.get_by_label(value)
        case "placeholder":
            return page.get_by_placeholder(value)
        case "role":
            name = selector["name"]
            return page.get_by_role(value, name=name)
        case "text":
            return page.get_by_text(value)
        case "title":
            return page.get_by_title(value)
        case "xpath":
            index = selector.get("index")
            locator = page.locator(value)
            return locator.nth(index) if index is not None else locator
        case _:
            return None

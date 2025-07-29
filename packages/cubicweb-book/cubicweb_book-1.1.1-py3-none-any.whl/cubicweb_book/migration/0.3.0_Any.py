add_attribute("Book", "pages")
add_attribute("Book", "publish_date")
rset = rql("Any B,N WHERE B nbe_pages N")
for book, pages in rset:
    rql("SET B pages %(p)s WHERE B eid %(x)s", {"p": int(pages), "x": book})
drop_attribute("Book", "nbe_pages")
sync_schema_props_perms("Book")
checkpoint()

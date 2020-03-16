import pusher

pusher_client = pusher.Pusher(
    app_id=u"963721",
    key=u"97bc56a1eb806d1e3cc9",
    secret=u"87f06f98f688bae03551",
    cluster=u"eu"
)

pusher_client.trigger(u'my-channel', u'my-event', {u'message': u'pene'})
// Initialize Pusher
    const pusher = new Pusher('97bc56a1eb806d1e3cc9', {
        cluster: 'eu',
        encrypted: true
    });

    // Subscribe to table channel
    var channel = pusher.subscribe('table');

    channel.bind('new-record', (data) => {
        $('#flights').append(`
            <tr id="${data.data.id} ">
                <th scope="row"> ${data.data.flight} </th>
                <td> ${data.data.destination} </td>
                <td> ${check_in} </td>
                <td> ${depature} </td>
                <td> ${data.data.status} </td>
            </tr>
       `)
    });

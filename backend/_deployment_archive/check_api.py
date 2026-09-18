import json
data = json.load(open('api_response.json', encoding='utf-8'))
with open('check_out.txt', 'w', encoding='utf-8') as f:
    for u in data['units']:
        if u['unit_no'] in ('214', '305'):
            f.write(f"Unit {u['unit_no']} - {u['building']}\n")
            for st in u['statuses']:
                f.write(f"  {st['date']}: {st['status']} (booking={st['booking_id']})\n")

import argparse, json, pprint, ast, sys
import jwt
from jwt.utils import base64url_decode

def parse_input(raw):
    try: return json.loads(raw)
    except: return ast.literal_eval(raw)

def is_jwt(token):
    try:
        parts = token.split('.')
        if len(parts) != 3: return False
        header = json.loads(base64url_decode(parts[0] + '=='))
        return 'alg' in header and 'typ' in header
    except: return False

def decode_jwts(obj):
    if isinstance(obj, dict):
        res = {}
        for k, v in obj.items():
            res[k] = decode_jwts(v)
            if isinstance(v, str) and is_jwt(v):
                try:
                    res[f"{k}__decoded"] = jwt.decode(v, options={"verify_signature": False})
                except Exception as e:
                    res[f"{k}__decoded_error"] = str(e)
        return res
    if isinstance(obj, list): return [decode_jwts(x) for x in obj]
    return obj

def main():
    parser = argparse.ArgumentParser(description='JSON/JWT formatter and decoder.')
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--file')
    group.add_argument('--json')
    group.add_argument('--input', action='store_true')
    parser.add_argument('--decode-jwt', action='store_true')
    parser.add_argument('--output')
    args = parser.parse_args()

    raw = open(args.file).read() if args.file else args.json or (print("Paste JSON (end Ctrl+D):") or sys.stdin.read())
    obj = parse_input(raw)
    if args.decode_jwt: obj = decode_jwts(obj)
    out = pprint.pformat(obj, indent=2, width=100)
    if args.output: open(args.output, 'w').write(out)
    else: print(out)

if __name__ == '__main__':
    main()

import { useSystemContext } from "~/context"
import DeviceIcon from "./device-icon";

export function Devices() {
    const system = useSystemContext();
    
    return (
        <div>
            Devices:
            <DeviceIcon device={system?.getCamera}/>
            <DeviceIcon device={system?.getPynq}/>
        </div>
    )
} 